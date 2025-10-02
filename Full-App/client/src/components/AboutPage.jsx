// AboutPage.jsx

import React from 'react';
import { Box, Container, Typography, Grid, Card, CardContent } from '@mui/material';

const AboutPage = () => {
  return (
    <Box sx={{ py: 8 }}>
      <Container maxWidth="lg">
        <Typography variant="h3" sx={{ mb: 4, fontWeight: 'bold', textAlign: 'center' }}>
          About LegallyTN
        </Typography>
        <Typography variant="body1" sx={{ mb: 6, textAlign: 'center' }}>
          LegallyTN is an advanced legal consulting chatbot designed to provide accessible and reliable guidance on Tunisian law. Our platform is powered by cutting-edge AI technology to offer 24/7 assistance for users in understanding various legal queries. Learn more about how LegallyTN can empower you with the knowledge you need.
        </Typography>
        
        {/* Features Section */}
        <Typography variant="h4" sx={{ mb: 4, fontWeight: 'bold' }}>
          Features
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%', backgroundColor: 'rgba(255, 255, 255, 0.9)', transition: 'transform 0.3s', '&:hover': { transform: 'translateY(-10px)' } }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" sx={{ mt: 2, mb: 1, color: '#ef4444' }}>
                  Expert Legal Guidance
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Access professional legal advice and consultation services for various Tunisian legal matters.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          {/* Add more feature cards here as needed */}
        </Grid>




      </Container>
    </Box>
  );
};

export default AboutPage;
