import os
import sys
import subprocess
import importlib

def install_and_import(package, module_name=None):
    """
    Tries to import the module. If it fails, installs the package and imports again.
    :param package: The package name to install via pip.
    :param module_name: The module name to import (if different from the package name).
    :return: The imported module.
    """
    try:
        if module_name is None:
            return importlib.import_module(package)
        else:
            return importlib.import_module(module_name)
    except ImportError:
        print(f"Package '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        if module_name is None:
            return importlib.import_module(package)
        else:
            return importlib.import_module(module_name)

# Install and import necessary libraries
# Note: 'os' is built-in so we do not need to install it.
pymongo = install_and_import("pymongo")
from pymongo import MongoClient

sentence_transformers = install_and_import("sentence-transformers", "sentence_transformers")
from sentence_transformers import SentenceTransformer

tqdm_module = install_and_import("tqdm")
from tqdm.auto import tqdm

torch = install_and_import("torch")

# Define the code name translations dictionary
CODE_NAME_TRANSLATIONS = {
    "code-aeronautique-civile": "Civil Aviation Code - Code de l'Aviation Civile - مجلة الطيران المدني",
    "code-amenagement-territoire-urbanisme": "Urban Planning and Land Management Code - Code de l'Aménagement du Territoire et de l'Urbanisme - مجلة التهيئة الترابية والتعمير",
    "code-arbitrage": "Arbitration Code - Code de l'Arbitrage - مجلة التحكيم",
    "code-assurances": "Insurance Code - Code des Assurances - مجلة التأمين",
    "code-changes-commerce-exterieur": "Foreign Exchange and Foreign Trade Code - Code des Changes et du Commerce Extérieur - مجلة الصرف والتجارة الخارجية",
    "code-collectivites-locales": "Local Authorities Code - Code des Collectivités Locales - مجلة الجماعات المحلية",
    "code-commerce-maritime": "Maritime Commerce Code - Code du Commerce Maritime - مجلة التجارة البحرية",
    "code-compatibilite-publique": "Public Accounting Code - Code de la Comptabilité Publique - مجلة المحاسبة العمومية",
    "code-conduite-deontologie-agent-public": "Code of Conduct for Public Agents - Code de Conduite et de Déontologie de l'Agent Public - مجلة سلوك وأخلاقيات العون العمومي",
    "code-decorations": "Decorations Code - Code des Décorations - مجلة الأوسمة",
    "code-deontologie-medecin-veterinaire": "Veterinary Ethics Code - Code de Déontologie du Médecin Vétérinaire - مجلة أخلاقيات الطبيب البيطري",
    "code-deontologie-medicale": "Medical Ethics Code - Code de Déontologie Médicale - مجلة أخلاقيات الطب",
    "code-devoirs-architectes": "Architects' Duties Code - Code des Devoirs des Architectes - مجلة واجبات المهندسين المعماريين",
    "code-disciplinaire-penal-maritime": "Maritime Disciplinary and Penal Code - Code Disciplinaire et Pénal Maritime - مجلة التأديب والجزاءات البحرية",
    "code-douanes": "Customs Code - Code des Douanes - مجلة الديوانة",
    "code-droit-international-prive": "Private International Law Code - Code de Droit International Privé - مجلة القانون الدولي الخاص",
    "code-droits-enregistrement-timbre": "Registration and Stamp Duties Code - Code des Droits d'Enregistrement et de Timbre - مجلة معاليم التسجيل والطابع الجبائي",
    "code-droits-procedures-fiscaux": "Tax Procedures Code - Code des Droits et Procédures Fiscaux - مجلة الحقوق والإجراءات الجبائية",
    "code-droits-reels": "Real Rights Code - Code des Droits Réels - مجلة الحقوق العينية",
    "code-eaux": "Water Code - Code des Eaux - مجلة المياه",
    "code-fiscalite-locale": "Local Taxation Code - Code de la Fiscalité Locale - مجلة الجباية المحلية",
    "code-forestier": "Forestry Code - Code Forestier - مجلة الغابات",
    "code-hydrocarbures": "Hydrocarbons Code - Code des Hydrocarbures - مجلة المحروقات",
    "code-impot-sur-revenu-personnes-physiques-impot-sur-les-societes": "Personal Income Tax and Corporate Tax Code - Code de l'Impôt sur le Revenu des Personnes Physiques et de l'Impôt sur les Sociétés - مجلة الضريبة على دخل الأشخاص الطبيعيين والضريبة على الشركات",
    "code-incitation-aux-investissements": "Investment Incentives Code - Code des Incitations aux Investissements - مجلة تشجيع الاستثمارات",
    "code-industrie-cinematographique": "Cinematographic Industry Code - Code de l'Industrie Cinématographique - مجلة الصناعة السينمائية",
    "code-justice-militaire": "Military Justice Code - Code de la Justice Militaire - مجلة القضاء العسكري",
    "code-minier": "Mining Code - Code Minier - مجلة المناجم",
    "code-nationalite": "Nationality Code - Code de la Nationalité - مجلة الجنسية",
    "code-obligations-contrats": "Obligations and Contracts Code - Code des Obligations et des Contrats - مجلة الالتزامات والعقود",
    "code-organismes-placement-collectif": "Collective Investment Schemes Code - Code des Organismes de Placement Collectif - مجلة هيئات الاستثمار الجماعي",
    "code-patrimoine-archeologique-historique-arts-traditionnels": "Archaeological, Historical, and Traditional Arts Heritage Code - Code du Patrimoine Archéologique, Historique et des Arts Traditionnels - مجلة حماية التراث الأثري والتاريخي والفنون التقليدية",
    "code-pecheur": "Fisheries Code - Code de la Pêche - مجلة الصيد البحري",
    "code-penal": "Penal Code - Code Pénal - المجلة الجزائية",
    "code-police-administrative-navigation-maritime": "Administrative Police of Maritime Navigation Code - Code de la Police Administrative de la Navigation Maritime - مجلة الشرطة الإدارية للملاحة البحرية",
    "code-ports-maritimes": "Maritime Ports Code - Code des Ports Maritimes - مجلة الموانئ البحرية",
    "code-poste": "Postal Code - Code de la Poste - مجلة البريد",
    "code-presse": "Press Code - Code de la Presse - مجلة الصحافة",
    "code-prestation-services-financiers-aux-non-residents": "Provision of Financial Services to Non-Residents Code - Code de la Prestation des Services Financiers aux Non-Résidents - مجلة تقديم الخدمات المالية لغير المقيمين",
    "code-procedure-civile-commerciale": "Civil and Commercial Procedure Code - Code de Procédure Civile et Commerciale - مجلة المرافعات المدنية والتجارية",
    "code-procedure-penale": "Criminal Procedure Code - Code de Procédure Pénale - مجلة الإجراءات الجزائية",
    "code-protection-enfant": "Child Protection Code - Code de la Protection de l'Enfant - مجلة حماية الطفل",
    "code-route": "Highway Code - Code de la Route - مجلة الطرقات",
    "code-societes-commerciales": "Commercial Companies Code - Code des Sociétés Commerciales - مجلة الشركات التجارية",
    "code-statut-personnel": "Personal Status Code - Code du Statut Personnel - مجلة الأحوال الشخصية",
    "code-taxe-sur-valeur-ajoutee": "Value Added Tax Code - Code de la Taxe sur la Valeur Ajoutée - مجلة الأداء على القيمة المضافة",
    "code-telecommunications": "Telecommunications Code - Code des Télécommunications - مجلة الاتصالات",
    "code-travail": "Labor Code - Code du Travail - مجلة الشغل",
    "code-travail-maritime": "Maritime Labor Code - Code du Travail Maritime - مجلة العمل البحري",
    "tunisian_constitution_articles": "Tunisian Constitution Articles - Articles de la Constitution Tunisienne - فصول الدستور التونسي"
}

# Initialize MongoDB connection and check/create database "rag_system_project"
client = MongoClient("mongodb://localhost:27017/")
db_name = "rag_system_project"
if db_name in client.list_database_names():
    db = client[db_name]
    print(f"Database '{db_name}' exists. Using it.")
else:
    db = client[db_name]
    print(f"Database '{db_name}' not found. Creating it.")

# Select (or create) the collection
collection = db["articles"]

# Initialize embedding model with GPU support (if available)
device = 'cuda' if torch.cuda.is_available() else 'cpu'
embedding_model = SentenceTransformer('sentence-transformers/multi-qa-mpnet-base-dot-v1', device=device)
print(f"Using device: {device}")

def process_and_embed_code_directory(code_directory, batch_size=16):
    """
    Processes a given code directory, computes embeddings in batches, and inserts the data into MongoDB.
    
    Parameters:
        code_directory (str): The path to the code directory.
        batch_size (int): The number of documents to process in each embedding batch.
    """
    code_name = os.path.basename(code_directory)  # Code name is the folder name
    code_translation = CODE_NAME_TRANSLATIONS.get(code_name, code_name)  # Get translation if available
    documents = []  # Temporary storage for documents to insert

    # Process each file in the directory
    for file_name in os.listdir(code_directory):
        if not file_name.endswith(".txt"):
            continue

        # Determine the article name
        article_number = file_name.split('.')[0]
        article_name = f"Article {article_number}"  # Example: Article 1

        # Read Arabic content
        arabic_file_path = os.path.join(code_directory, file_name)
        with open(arabic_file_path, "r", encoding="utf-8") as arabic_file:
            arabic_content = arabic_file.read().strip()

        # Find the translated English file
        translated_folder_path = os.path.join(code_directory, "translated")
        translated_file_name = file_name.replace(".txt", "_translated.txt")
        translated_file_path = os.path.join(translated_folder_path, translated_file_name)

        if not os.path.isfile(translated_file_path):
            print(f"Translated file not found: {translated_file_path}")
            continue

        # Read English content
        with open(translated_file_path, "r", encoding="utf-8") as translated_file:
            english_content = translated_file.read().strip()

        # Add code name and article name to the content
        arabic_content = f"{code_translation.split(' - ')[-1]} - الفصل {article_number}\n{arabic_content}"
        english_content = f"{code_translation.split(' - ')[0]} - {article_name}\n{english_content}"

        # Prepare the document
        document = {
            "code_name": code_name,
            "article_name": article_name,
            "content_arabic": arabic_content,
            "content_english": english_content,
        }
        documents.append(document)

    # Batch process embeddings for English content
    content_batch = [doc["content_english"] for doc in documents]
    embeddings = embedding_model.encode(
        content_batch,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=True,
        normalize_embeddings=True  # Normalize for consistency with retrieval pipeline
    )

    # Add embeddings and insert documents into MongoDB
    for doc, embedding in zip(documents, embeddings):
        doc["embedding_english"] = embedding.tolist()

        # Avoid duplicate inserts
        if collection.find_one({"code_name": doc["code_name"], "article_name": doc["article_name"]}):
            print(f"Document already exists: {doc['article_name']} in {doc['code_name']}")
            continue

        collection.insert_one(doc)

    print(f"The following code has been processed, embedded, and inserted: {code_name}")

def process_all_code_directories(base_directory, batch_size=16):
    """
    Processes all code directories within the given base directory.
    
    Parameters:
        base_directory (str): The path to the base directory containing code directories.
        batch_size (int): The number of documents to process in each embedding batch.
    """
    for folder_name in os.listdir(base_directory):
        code_directory = os.path.join(base_directory, folder_name)
        if os.path.isdir(code_directory):
            print(f"Processing code directory: {folder_name}")
            process_and_embed_code_directory(code_directory, batch_size=batch_size)

# Set the base directory relative to this script (Database folder is alongside this file)
base_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data base")
process_all_code_directories(base_directory, batch_size=16)
