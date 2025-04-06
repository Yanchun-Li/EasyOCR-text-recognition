import React, { useState, useRef } from 'react';
import { Box, Button, Typography, CircularProgress, Alert, FormControl, FormLabel, RadioGroup, FormControlLabel, Radio, Divider } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const ImageUploader = ({ onImageUpload }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [engine, setEngine] = useState('local'); // Default to local model
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      handleFile(file);
    } else {
      setError('Please upload an image file');
    }
  };

  const handleFileInput = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFile(file);
    }
  };

  const handleEngineChange = (e) => {
    setEngine(e.target.value);
  };

  const handleFile = async (file) => {
    setIsLoading(true);
    setError(null);
    try {
      // Create preview URL
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('engine', engine); // Add engine selection to form data
      
      console.log('Sending file to server:', file.name, 'with engine:', engine);
      const response = await fetch('http://localhost:5000/ocr', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Received response:', data);
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      onImageUpload(data);
    } catch (error) {
      console.error('Error uploading file:', error);
      setError(error.message || 'Error processing image');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box>
      <FormControl component="fieldset" sx={{ mb: 3, width: '100%' }}>
        <FormLabel component="legend">Select OCR Engine</FormLabel>
        <RadioGroup
          row
          aria-label="ocr-engine"
          name="ocr-engine"
          value={engine}
          onChange={handleEngineChange}
        >
          <FormControlLabel value="local" control={<Radio />} label="Local Model" />
          <FormControlLabel value="easyocr" control={<Radio />} label="EasyOCR" />
        </RadioGroup>
      </FormControl>
      
      <Divider sx={{ mb: 3 }} />
      
      <Box
        sx={{
          border: '2px dashed',
          borderColor: isDragging ? 'primary.main' : 'grey.300',
          borderRadius: 2,
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          '&:hover': {
            borderColor: 'primary.main',
          },
          mb: 2,
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          accept="image/*"
          style={{ display: 'none' }}
          ref={fileInputRef}
          onChange={handleFileInput}
        />
        {isLoading ? (
          <CircularProgress />
        ) : (
          <>
            <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
            <Typography variant="h6" gutterBottom>
              Drag and drop an image here
            </Typography>
            <Typography variant="body2" color="text.secondary">
              or click to select a file
            </Typography>
          </>
        )}
      </Box>
      {previewUrl && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <img 
            src={previewUrl} 
            alt="Preview" 
            style={{ 
              maxWidth: '100%', 
              maxHeight: '300px',
              borderRadius: '8px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }} 
          />
        </Box>
      )}
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  );
};

export default ImageUploader; 