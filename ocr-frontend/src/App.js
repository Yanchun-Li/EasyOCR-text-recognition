import React, { useState } from 'react';
import { Container, Typography, Box, CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import ImageUploader from './components/ImageUploader';
import ResultDisplay from './components/ResultDisplay';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#9c27b0',
    },
  },
});

function App() {
  const [result, setResult] = useState(null);

  const handleImageUpload = (data) => {
    setResult(data);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="md">
        <Box sx={{ my: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            OCR Text Recognition
          </Typography>
          <Typography variant="subtitle1" align="center" color="text.secondary" paragraph>
            Upload an image to recognize text with confidence levels
          </Typography>
          <ImageUploader onImageUpload={handleImageUpload} />
          <ResultDisplay result={result} />
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
