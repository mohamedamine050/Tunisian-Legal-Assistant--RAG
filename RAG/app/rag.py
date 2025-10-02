# app/rag.py

import os
import torch
import numpy as np
import faiss
import nltk
import wn
import google.generativeai as genai
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
from nltk.tokenize import word_tokenize, PunktSentenceTokenizer
from tqdm.auto import tqdm
from dotenv import load_dotenv
import logging
from typing import List
from app.models import Message

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# -----------------------------------
# Configuration and Initialization
# -----------------------------------

# Initialize MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
MONGODB_DB = os.getenv('MONGODB_DB', 'rag_system_project')
MONGODB_COLLECTION = os.getenv('MONGODB_COLLECTION', 'articles')

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]
collection = db[MONGODB_COLLECTION]

# Initialize Google Generative AI with your API key
GENAI_API_KEY = os.getenv('GENAI_API_KEY')
if not GENAI_API_KEY:
    raise ValueError("Google Generative AI API key not found in environment variables.")
genai.configure(api_key=GENAI_API_KEY)

# Download Open English WordNet
wn.download('oewn:2021')  # 'oewn' is the correct identifier for Open English WordNet

import os

# Ensure NLTK uses the correct local path
nltk_path = os.path.join(os.getcwd(), "venv", "nltk_data")
if nltk_path not in nltk.data.path:
    nltk.data.path.insert(0, nltk_path)

# Log final search paths
logger.info(f"Final NLTK search paths: {nltk.data.path}")

# Download `punkt` inside venv
nltk.download('punkt', download_dir=nltk_path)
nltk.download('punkt_tab', download_dir=nltk_path)

# Verify where `punkt` is actually loaded from
try:
    punkt_path = nltk.data.find('tokenizers/punkt')
    logger.info(f"NLTK 'punkt' tokenizer found at: {punkt_path}")
except LookupError:
    logger.error("NLTK 'punkt' tokenizer NOT found!")

# Initialize embedding models
device = 'cuda' if torch.cuda.is_available() else 'cpu'
logger.info(f"Using device: {device}")

embedding_model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1', device=device)
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-12-v2')

# Initialize tokenizer for BM25
tokenizer = PunktSentenceTokenizer()

# Global variables for documents and indexes
documents_mapping = {}
documents = []
embeddings = None
index = None
bm25 = None
tokenized_corpus = []
document_code_mapping = []  # To map each document to its code(s)

# -----------------------------------
# Helper Functions
# -----------------------------------

def document_routing(query):
    """
    Routes a query into relevant Tunisian legal codes by using the Gemini model.
    The output is a list of exact names of relevant codes, separated by spaces.

    Parameters:
    query (str): The legal query for which relevant codes need to be identified.

    Returns:
    list: A list of relevant Tunisian legal codes separated by spaces.
    """

    gemini_input = f"""
You are a legal assistant. Your task is to analyze the query and determine 
which of the following Tunisian legal codes are relevant to it. Return the 
exact names of the relevant or relating codes provided in the list, separated by spaces. 
Do not add any additional text or modify the code names.
in case you did not find related code return the word "answer.

Here are the Tunisian legal codes with descriptions:
- code-aeronautique-civile: Governs regulations related to civil aviation, including air travel, aviation safety, and airspace management.
- code-amenagement-territoire-urbanisme: Covers rules related to urban planning and land management, ensuring sustainable and organized territorial development.
- code-arbitrage: Regulates arbitration processes for resolving disputes outside of court.
- code-assurances: Governs insurance policies, companies, and obligations in Tunisia.
- code-changes-commerce-exterieur: Deals with foreign trade policies and currency exchange regulations.
- code-collectivites-locales: Outlines laws related to local government administration and responsibilities.
- code-commerce-maritime: Regulates maritime trade, shipping operations, and associated commercial activities.
- code-compatibilite-publique: Governs public accounting and management of state funds.
- code-conduite-deontologie-agent-public: Sets ethical rules and professional conduct standards for public servants.
- code-decorations: Outlines laws regarding state decorations, medals, and honors.
- code-deontologie-medecin-veterinaire: Defines professional standards and ethics for veterinary medicine practitioners.
- code-deontologie-medicale: Regulates ethical conduct and responsibilities of medical professionals.
- code-devoirs-architectes: Details professional obligations and ethical standards for architects.
- code-disciplinaire-penal-maritime: Covers disciplinary and penal matters related to maritime operations.
- code-douanes: Governs customs duties, import/export regulations, and border control.
- code-droit-international-prive: Regulates private international law matters, such as conflicts of law and cross-border disputes.
- code-droits-enregistrement-timbre: Governs the registration and stamp duties in financial and legal transactions.
- code-droits-procedures-fiscaux: Covers tax procedures and fiscal obligations.
- code-droits-reels: Governs real property rights, including ownership, mortgages, and easements.
- code-eaux: Manages water resources, usage, and conservation laws.
- code-fiscalite-locale: Covers taxation and fiscal management at the local government level.
- code-forestier: Protects and regulates forest areas, logging activities, and wildlife preservation.
- code-hydrocarbures: Governs exploration, production, and management of hydrocarbons in Tunisia.
- code-impot-sur-revenu-personnes-physiques-impot-sur-les-societes: Covers personal and corporate income tax regulations.
- code-incitation-aux-investissements: Provides rules to encourage domestic and foreign investments in Tunisia.
- code-industrie-cinematographique: Regulates the cinematic industry, including production, distribution, and exhibition of films.
- code-justice-militaire: Covers legal matters and regulations within the military justice system.
- code-minier: Regulates mining operations, mineral rights, and related activities.
- code-nationalite: Defines laws related to Tunisian nationality, acquisition, and loss of citizenship.
- code-obligations-contrats: Governs contracts, obligations, and related civil matters.
- code-organismes-placement-collectif: Regulates collective investment schemes and funds management.
- code-patrimoine-archeologique-historique-arts-traditionnels: Protects archaeological and historical heritage sites in Tunisia.
- code-pecheur: Covers fishing regulations, rights, and resource management for fisheries.
- code-penal: Governs criminal law and procedures, defining offenses and their penalties.
- code-police-administrative-navigation-maritime: Manages administrative police duties related to maritime navigation.
- code-ports-maritimes: Regulates the operation and management of maritime ports.
- code-poste: Governs postal services, including mail delivery and related activities.
- code-presse: Covers press freedom, media laws, and publication regulations.
- code-prestation-services-financiers-aux-non-residents: Regulates financial services provided to non-residents.
- code-procedure-civile-commerciale: Governs civil and commercial legal procedures in courts.
- code-procedure-penale: Covers criminal procedure and the administration of justice.
- code-protection-enfant: Protects children's rights and welfare in Tunisia.
- code-route: Contains rules and regulations for road traffic, vehicle operations, and driving safety.
- code-societes-commerciales: Regulates the formation, operation, and dissolution of commercial companies.
- code-statut-personnel: Governs family law, including marriage, divorce, and inheritance.
- code-taxe-sur-valeur-ajoutee: Regulates the application and administration of value-added tax (VAT).
- code-telecommunications: Covers telecommunications operations, infrastructure, and related services.
- code-travail: Governs labor laws, including employment contracts, workers' rights, and workplace regulations.
- code-travail-maritime: Regulates working conditions, rights, and obligations of maritime workers.
- tunisian_constitution_articles: Refers to the articles of the Tunisian Constitution, including fundamental rights, governance, and legal structure and general info about tunisia's values and info.

Query:
{query}

Answer:
"""

    # Instantiate the Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Generate a response
    response = model.generate_content(gemini_input)

    # Print and return the response as a list of codes
    logger.info(f"Document Routing Response: {response.text}")
    if "answer" in response.text.lower() :
        return []
    return list(response.text.split())

def query_expansion(query):
    """
    Expand the query using synonyms from WordNet (using the `wn` library).
    """
    synonyms = set()
    for word in nltk.word_tokenize(query):
        for synset in wn.synsets(word):
            for lemma in synset.lemmas():  # Corrected: Added parentheses to call the method
                synonym = lemma.replace('_', ' ')
                if synonym.lower() != word.lower():
                    synonyms.add(synonym)
    expanded_query = query + ' ' + ' '.join(synonyms)
    return expanded_query

def mmr(query_embedding, doc_embeddings, documents, top_k, diversity=0.7):
    """
    Calculate Maximal Marginal Relevance (MMR) to diversify the results.
    """
    # Calculate similarity between query and documents
    doc_similarities = np.dot(doc_embeddings, query_embedding.T).flatten()

    # Initialize list of selected documents and their embeddings
    selected_docs = []
    selected_indices = []

    for _ in range(top_k):
        if len(selected_docs) == 0:
            # Select the document with the highest similarity
            idx = np.argmax(doc_similarities)
            selected_docs.append(documents[idx])
            selected_indices.append(idx)
        else:
            # Calculate MMR
            mmr_scores = []
            for idx in range(len(documents)):
                if idx in selected_indices:
                    continue
                relevance = doc_similarities[idx]
                diversity_scores = max(
                    [np.dot(doc_embeddings[idx], doc_embeddings[i]) for i in selected_indices]
                )
                mmr_score = diversity * relevance - (1 - diversity) * diversity_scores
                mmr_scores.append((idx, mmr_score))
            if not mmr_scores:
                break
            # Select document with highest MMR score
            idx, _ = max(mmr_scores, key=lambda x: x[1])
            selected_docs.append(documents[idx])
            selected_indices.append(idx)

    return selected_docs
def early_response(query, conversation):
    gemini_input = f"""You are a conversation classifier for a legal assistant system. Analyze if this interaction requires legal expertise or is casual conversation.

Query: "{query}"

Previous Conversation:
{conversation}

Classification Rules:
1. CASUAL CONVERSATION (Respond with FALSE):
   - Personal introductions (e.g., "My name is...", "Nice to meet you")
   - General greetings (e.g., "Hello", "How are you")
   - Small talk (e.g., "What's the weather like", "How's your day")
   - Gratitude expressions (e.g., "Thank you", "Thanks")
   - Personal statements unrelated to legal matters
   - Casual questions about the AI itself
   - Farewell messages (e.g., "Goodbye", "See you later")

2. LEGAL QUERIES (Respond with TRUE):
   - Questions about Tunisian laws or regulations
   - Inquiries about legal procedures
   - Questions about rights and obligations
   - Requests for legal document interpretation
   - Legal status inquiries
   - Questions about court procedures
   - Regulatory compliance questions
   - Follow-up questions to previous legal discussions

Example Classifications:
- "My name is Ahmed" → FALSE Nice to meet you Ahmed! How can I assist you today?
- "Tell me more about article 4" → TRUE
- "What's your name?" → FALSE I'm your AI legal assistant, you can call me HouyemAI.
- "How do I file for divorce?" → TRUE
- "Thanks for the help" → FALSE You're welcome! Let me know if you need any other assistance.
- "What are the requirements?" → TRUE (if in legal context) / FALSE (if no legal context)

Format your response exactly as:
FALSE <friendly response>  (for casual conversation)
TRUE  (for legal queries)

Evaluate the current query and respond accordingly:"""

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(gemini_input)
    
    try:
        response_text = response.text.strip()
        if response_text.lower().startswith("false"):
            return ["FALSE", response_text[5:].strip()]
        else:
            return ["TRUE", ""]
    except:
        return ["TRUE", ""]


def detect_language_and_translate(query):
    """Helper function to detect language and translate if needed"""
    gemini_input = f"""Analyze the following query:
"{query}"
If the query is in Arabic or contains Arabic script, translate it to English and return exactly in this format:
ARABIC  <english translation>
If the query is in English or any other non-Arabic script, return exactly in this format:
ENGLISH
Only return the array format described above, nothing else."""

    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(gemini_input)
    try:
        if response.text.lower()[:3]=="ara" :
            return ["ARABIC",response.text[6:]]
        else :
            return ["ENGLISH", query]
    except:
        return ["ENGLISH", query]

def retrieve_documents(query, top_k=5):
    """
    Retrieve documents using document routing, BM25, and FAISS.
    """


    # 1. Document Routing to get relevant legal codes
    relevant_codes = document_routing(query)
    logger.info(f"Relevant Legal Codes: {relevant_codes}")

    if not relevant_codes:
        logger.warning("No relevant legal codes found. Falling back to all documents.")
        relevant_indices = list(range(len(documents)))
    else:
        # 2. Filter documents based on relevant codes
        relevant_indices = [
            idx for idx, code in enumerate(document_code_mapping)
            if code in relevant_codes
        ]
        logger.info(f"Number of relevant documents: {len(relevant_indices)}")

    if not relevant_indices:
        logger.warning("No documents found for the relevant codes.")
        return []

    # 3. Perform BM25 retrieval on the filtered documents
    expanded_query = query_expansion(query)
    tokenized_query = nltk.word_tokenize(expanded_query.lower())
    bm25_scores = bm25.get_scores(tokenized_query)

    # Filter BM25 scores based on relevant indices
    bm25_scores_filtered = [bm25_scores[idx] for idx in relevant_indices]
    bm25_top_n = np.argsort(bm25_scores_filtered)[::-1][:top_k * 10]
    bm25_selected_indices = [relevant_indices[i] for i in bm25_top_n]
    bm25_docs = [documents[i] for i in bm25_selected_indices]
    bm25_embeddings = embeddings[bm25_selected_indices]

    # 4. Perform FAISS retrieval on the filtered documents
    query_embedding = embedding_model.encode(
        expanded_query,
        convert_to_numpy=True,
        normalize_embeddings=True  # Ensure embeddings are not normalized
    )
    distances, indices = index.search(query_embedding.reshape(1, -1), top_k * 10)

    # Map FAISS indices back to original document indices
    faiss_selected_indices = [relevant_indices[i] for i in indices[0] if i < len(relevant_indices)]
    faiss_docs = [documents[i] for i in faiss_selected_indices]
    faiss_embeddings = embeddings[faiss_selected_indices]

    # 5. Combine BM25 and FAISS results while avoiding duplicates
    combined_docs = []
    combined_embeddings = []

    for doc, emb in zip(bm25_docs + faiss_docs, np.vstack((bm25_embeddings, faiss_embeddings))):
        if doc not in combined_docs:
            combined_docs.append(doc)
            combined_embeddings.append(emb)

    combined_embeddings = np.array(combined_embeddings)

    if not combined_docs:
        logger.warning("No documents retrieved after combining BM25 and FAISS results.")
        return []

    # 6. Apply MMR to select diverse and relevant documents
    mmr_docs = mmr(query_embedding, combined_embeddings, combined_docs, top_k=top_k)

    # 7. Re-rank with CrossEncoder
    query_doc_pairs = [(query, doc) for doc in mmr_docs]
    rerank_scores = cross_encoder.predict(query_doc_pairs)

    # Normalize re-rank scores
    if rerank_scores.max() != rerank_scores.min():
        rerank_scores_norm = (rerank_scores - rerank_scores.min()) / (rerank_scores.max() - rerank_scores.min())
    else:
        rerank_scores_norm = rerank_scores

    # Sort documents by re-rank scores
    doc_score_pairs = sorted(
        zip(mmr_docs, rerank_scores_norm),
        key=lambda x: x[1],
        reverse=True
    )

    return doc_score_pairs
def make_query_better(query, conversation):


    gemini_input = f"""You are a query enhancement system. Your task is to transform the given query by incorporating relevant context from the conversation history. Pay special attention to:
    1. References to previous topics or articles
    2. Follow-up questions like "tell me more" or "analyze this"
    3. Requests for specific details mentioned earlier
    4. Implicit references that need context

    Examples of transformations:
    - If query is "analyze this further" and previous context discussed divorce procedures, transform to "what are the detailed legal procedures for divorce in Tunisia"
    - If query is "what about the fourth article" and context discussed traffic laws, transform to "what are the specific requirements and regulations in article 4 of the traffic law regarding road safety"
    - If query is "tell me more" and context discussed business registration, transform to "what are the detailed requirements and procedures for registering a business in Tunisia"
    - If query is "what are my rights" and context discussed workplace discrimination, transform to "what are the legal rights and protections for employees facing workplace discrimination under Tunisian labor law"

    Current Context:
    Query: {query}

    Conversation History:
    {conversation}

    Create a comprehensive search query that:
    - Captures the full context of the discussion
    - Resolves any references to previous topics
    - Expands abbreviated or implicit requests
    - Translates legal code references into natural language topics
    - Maintains focus on Tunisian legal framework

    Your task is to generate ONE clear, specific query that will help retrieve relevant legal information from our database of Tunisian legal codes and regulations.

    Database coverage includes topics like:
- code-aeronautique-civile: Governs regulations related to civil aviation, including air travel, aviation safety, and airspace management.
- code-amenagement-territoire-urbanisme: Covers rules related to urban planning and land management, ensuring sustainable and organized territorial development.
- code-arbitrage: Regulates arbitration processes for resolving disputes outside of court.
- code-assurances: Governs insurance policies, companies, and obligations in Tunisia.
- code-changes-commerce-exterieur: Deals with foreign trade policies and currency exchange regulations.
- code-collectivites-locales: Outlines laws related to local government administration and responsibilities.
- code-commerce-maritime: Regulates maritime trade, shipping operations, and associated commercial activities.
- code-compatibilite-publique: Governs public accounting and management of state funds.
- code-conduite-deontologie-agent-public: Sets ethical rules and professional conduct standards for public servants.
- code-decorations: Outlines laws regarding state decorations, medals, and honors.
- code-deontologie-medecin-veterinaire: Defines professional standards and ethics for veterinary medicine practitioners.
- code-deontologie-medicale: Regulates ethical conduct and responsibilities of medical professionals.
- code-devoirs-architectes: Details professional obligations and ethical standards for architects.
- code-disciplinaire-penal-maritime: Covers disciplinary and penal matters related to maritime operations.
- code-douanes: Governs customs duties, import/export regulations, and border control.
- code-droit-international-prive: Regulates private international law matters, such as conflicts of law and cross-border disputes.
- code-droits-enregistrement-timbre: Governs the registration and stamp duties in financial and legal transactions.
- code-droits-procedures-fiscaux: Covers tax procedures and fiscal obligations.
- code-droits-reels: Governs real property rights, including ownership, mortgages, and easements.
- code-eaux: Manages water resources, usage, and conservation laws.
- code-fiscalite-locale: Covers taxation and fiscal management at the local government level.
- code-forestier: Protects and regulates forest areas, logging activities, and wildlife preservation.
- code-hydrocarbures: Governs exploration, production, and management of hydrocarbons in Tunisia.
- code-impot-sur-revenu-personnes-physiques-impot-sur-les-societes: Covers personal and corporate income tax regulations.
- code-incitation-aux-investissements: Provides rules to encourage domestic and foreign investments in Tunisia.
- code-industrie-cinematographique: Regulates the cinematic industry, including production, distribution, and exhibition of films.
- code-justice-militaire: Covers legal matters and regulations within the military justice system.
- code-minier: Regulates mining operations, mineral rights, and related activities.
- code-nationalite: Defines laws related to Tunisian nationality, acquisition, and loss of citizenship.
- code-obligations-contrats: Governs contracts, obligations, and related civil matters.
- code-organismes-placement-collectif: Regulates collective investment schemes and funds management.
- code-patrimoine-archeologique-historique-arts-traditionnels: Protects archaeological and historical heritage sites in Tunisia.
- code-pecheur: Covers fishing regulations, rights, and resource management for fisheries.
- code-penal: Governs criminal law and procedures, defining offenses and their penalties.
- code-police-administrative-navigation-maritime: Manages administrative police duties related to maritime navigation.
- code-ports-maritimes: Regulates the operation and management of maritime ports.
- code-poste: Governs postal services, including mail delivery and related activities.
- code-presse: Covers press freedom, media laws, and publication regulations.
- code-prestation-services-financiers-aux-non-residents: Regulates financial services provided to non-residents.
- code-procedure-civile-commerciale: Governs civil and commercial legal procedures in courts.
- code-procedure-penale: Covers criminal procedure and the administration of justice.
- code-protection-enfant: Protects children's rights and welfare in Tunisia.
- code-route: Contains rules and regulations for road traffic, vehicle operations, and driving safety.
- code-societes-commerciales: Regulates the formation, operation, and dissolution of commercial companies.
- code-statut-personnel: Governs family law, including marriage, divorce, and inheritance.
- code-taxe-sur-valeur-ajoutee: Regulates the application and administration of value-added tax (VAT).
- code-telecommunications: Covers telecommunications operations, infrastructure, and related services.
- code-travail: Governs labor laws, including employment contracts, workers' rights, and workplace regulations.
- code-travail-maritime: Regulates working conditions, rights, and obligations of maritime workers.
- tunisian_constitution_articles: Refers to the articles of the Tunisian Constitution, including fundamental rights, governance, and legal structure and general info about tunisia's values and info.

    ONLY RETURN THE ENHANCED QUERY, NOTHING ELSE
    Enhanced Query:"""

    # Instantiate the Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    # Generate a response
    response = model.generate_content(gemini_input)


    return response.text

def rag_system(query, top_k=5, memory: List[Message] = None):
    """
    Retrieval-Augmented Generation system with Gemini filtering.
    """
    try:
        logger.info(f"Starting RAG system for query: {query}")
                # Format conversation history
        conversation_history = ""
        if memory and len(memory) > 0:
            conversation_history = "\nPrevious conversation:\n" + "\n".join([
                f"{'Human' if msg.role == 'user' else 'Assistant'}: {msg.content}"
                for msg in memory[-10:]  # Take last 10 messages
            ])
            logger.info("Added conversation history to context")
        logger.info("conversation history : " ,conversation_history)
        early_tag,early_rep=early_response(query,conversation_history)
        if early_tag=="FALSE" :
            return early_rep,[]
        logger.info("early tag :",early_tag)
        logger.info("early rep :",early_rep)
        # New Step: Detect language and translate if needed
        lang_tag, query = detect_language_and_translate(query)
        logger.info(f"Query language: {lang_tag}, Processed query: {query}")
        queryfinal=query
        query=make_query_better(query,conversation_history)
        logger.info("new query is : " , query)
        # Step 1: Retrieve and re-rank documents
        logger.info("Retrieving documents...")
        doc_score_pairs = retrieve_documents(query, top_k=top_k)
        logger.info(f"Retrieved {len(doc_score_pairs)} documents.")

        if not doc_score_pairs:
            logger.warning("No relevant documents found for the given query.")
            return "No relevant documents found for the given query.", ""

        # Step 2: Clean each document before including in context
        cleaned_docs = [doc.replace('## English Translation:', '').strip() for doc, _ in doc_score_pairs]
        scores = [score for _, score in doc_score_pairs]

        # Step 3: Prepare initial context for Gemini filtering
        initial_context = "\n\n".join([
            f"Document {i+1}:\n{doc}"
            for i, doc in enumerate(cleaned_docs)
        ])

        gemini_input = f"""Based on the following documents and the query, provide the indices of the **most relevant documents** as integers corresponding to their order in the list of documents. only exclude documents that are totally irrelevants don't be harsh. 
Include only the document indices in a comma-separated format.

Example format:
Relevant Document Indices:
[Index1, Index2, Index3]

---

Documents:
{initial_context}

Query:
{query}
"""
        logger.info("Sending initial context to Gemini for filtering relevant document indices...")

        # Step 4: Instantiate the Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # Step 5: Use Google Gemini to identify relevant document indices
        gemini_response = model.generate_content(gemini_input)
        response_text = gemini_response.text.strip()
        logger.info("Received response from Gemini.")

        try:
            indices_section = response_text.split("Relevant Document Indices:")[1].strip()
            relevant_indices = [
                int(idx.strip()) for idx in indices_section.strip("[]").split(",") if idx.strip().isdigit()
            ]
            
            # Handle case where no indices are found
            if not relevant_indices:
                no_relevant_msg = "While I found some documents, none seem directly relevant to your query. Could you please provide more specific details about what you're looking for?"
                if lang_tag.lower() == "arabic":
                    return translate_to_arabic(no_relevant_msg), []
                return no_relevant_msg, []
                
            logger.info(f"Relevant document indices identified: {relevant_indices}")
            
            # Filter and verify documents
            gemini_verified = [
                doc_score_pairs[idx - 1] for idx in relevant_indices
                if 1 <= idx <= len(doc_score_pairs)
            ]
            
            # Handle case where no documents pass verification
            if not gemini_verified:
                no_verified_msg = "I found some potential matches, but couldn't verify their relevance to your query. Could you please rephrase your question?"
                if lang_tag.lower() == "arabic":
                    return translate_to_arabic(no_verified_msg), []
                return no_verified_msg, []
                
        except (IndexError, ValueError) as e:
            logger.error(f"Error processing Gemini response: {e}")
            error_msg = "I encountered an issue processing your query. Could you please try asking in a different way?"
            if lang_tag.lower() == "arabic":
                return translate_to_arabic(error_msg), []
            return error_msg, []

        # Step 8: Sort the verified documents by score in descending order
        gemini_verified_sorted = sorted(gemini_verified, key=lambda x: x[1], reverse=True)
        logger.info("Sorted verified documents by score in descending order.")
        if lang_tag.lower() == "arabic" :
            logger.info("Converting documents to Arabic...")
            arabic_verified = []
            for doc, score in gemini_verified_sorted:
                arabic_content = documents_mapping.get(doc)
                if arabic_content:
                    logger.info(f"Found Arabic mapping for document")
                    arabic_verified.append((arabic_content, score))
                else:
                    logger.warning(f"Arabic mapping not found for document")
                    arabic_verified.append((doc, score))  # Fallback to English if no Arabic version
        # Step 9: Clean the verified documents (remove unwanted prefixes)
        cleaned_verified_docs = [
            doc.replace('## English Translation:', '').strip()
            for doc, _ in gemini_verified_sorted
        ]
        logger.info(cleaned_verified_docs)
        # Step 10: Prepare context without showing scores
        context = "\n\n".join([
            f"Document {i+1}:\n{doc}" 
            for i, doc in enumerate(cleaned_verified_docs)  
        ])
        logger.info("Prepared context with filtered and sorted documents.")
        logger.info(context)

        # Step 11: Prepare the prompt for Google Gemini to generate the final answer
        gemini_final_input = f"""As a legal assistant with expertise in Tunisian law, answer the following question based solely on the provided documents. Be concise and provide accurate information. Interpret those documents and be analytical and go into details.
conversation history :
{conversation_history}

Documents:
{context}

Question:
{queryfinal}

Answer:"""
        logger.info("Sending final context and query to Gemini for answer generation.")

        # Step 12: Use Google Gemini to generate the final answer
        final_response = model.generate_content(gemini_final_input)
        answer = final_response.text.strip() if final_response.text else "Gemini did not return a response. Please try again."
        logger.info("Final answer generated by Gemini.")
        # Step 13: Return the answer and the sorted, verified doc_score_pairs
        logger.info("original answer is : " ,answer )
        if lang_tag.lower() == "arabic":
            answer = translate_to_arabic(answer)
            return answer, arabic_verified
        return answer, gemini_verified_sorted


    except Exception as e:
        logger.error(f"An error occurred in rag_system: {e}", exc_info=True)
        return "An error occurred while processing your request.", ""


def initialize_rag_system():
    """
    Initialize the RAG system with English-Arabic content mapping
    """
    global documents, embeddings, index, bm25, tokenized_corpus, document_code_mapping, documents_mapping

    try:
        # Fetch all documents from MongoDB
        all_docs_cursor = collection.find({})

        # Extract documents, embeddings, and mappings
        documents = []
        embeddings_list = []
        document_code_mapping = []
        documents_mapping = {}  # Clear existing mapping

        logger.info("Fetching all documents and embeddings from MongoDB...")
        for doc in tqdm(all_docs_cursor, desc="Fetching"):
            content_en = doc.get("content_english", "")
            content_ar = doc.get("content_arabic", "")
            embedding = doc.get("embedding_english", [])
            code_name = doc.get("code_name", "")

            if content_en and embedding and code_name:
                # Store main English content and mappings
                documents.append(content_en)
                embeddings_list.append(embedding)
                document_code_mapping.append(code_name)
                
                # Store mapping between English and Arabic content
                if content_ar:
                    documents_mapping[content_en] = content_ar

        logger.info(f"Fetched {len(documents)} documents and built {len(documents_mapping)} language mappings.")

        # Rest of initialization remains the same...
        if not documents:
            logger.warning("No documents found in MongoDB.")
            return

        embeddings = np.array(embeddings_list).astype('float32')
        
        embedding_size = embeddings.shape[1]
        index = faiss.IndexFlatIP(embedding_size)
        index.add(embeddings)
        
        logger.info("Tokenizing documents for BM25...")
        tokenized_corpus = [word_tokenize(doc.lower()) for doc in tqdm(documents, desc="Tokenizing")]
        bm25 = BM25Okapi(tokenized_corpus)
        logger.info("BM25 index built.")

    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        raise e
def translate_to_arabic(text):
    """Helper function to translate text to Arabic using Gemini"""
    prompt = f"""Translate the following text to Arabic, maintaining legal terminology and professional tone:

{text}

Provide only the Arabic translation, nothing else."""
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()
