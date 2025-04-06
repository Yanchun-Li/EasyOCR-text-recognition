import React from 'react';
import { Box, Typography, Paper, Grid, Chip } from '@mui/material';

const ResultDisplay = ({ result }) => {
  if (!result) return null;

  const getConfidenceColor = (confidence) => {
    const value = confidence / 100;
    return `rgb(${255 * (1 - value)}, ${255 * value}, 0)`;
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Recognition Result
        </Typography>
        <Chip 
          label={result.engine === 'easyocr' ? 'EasyOCR' : 'Local Model'} 
          color={result.engine === 'easyocr' ? 'primary' : 'secondary'} 
          size="small" 
        />
      </Box>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box sx={{ 
            mt: 2,
            p: 2,
            backgroundColor: 'grey.50',
            borderRadius: 1,
            minHeight: '100px'
          }}>
            {result.result.map((item, index) => (
              <Box
                key={index}
                sx={{
                  display: 'inline-block',
                  p: 0.5,
                  m: 0.5,
                  borderRadius: 1,
                  backgroundColor: getConfidenceColor(item.confidence),
                }}
              >
                <Typography variant="body1">
                  {item.text}
                </Typography>
              </Box>
            ))}
          </Box>
        </Grid>
        <Grid item xs={12}>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Confidence Level Indicator:
            </Typography>
            <Box
              sx={{
                height: 20,
                background: 'linear-gradient(to right, rgb(255,0,0), rgb(255,255,0), rgb(0,255,0))',
                borderRadius: 1,
                mt: 1,
              }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
              <Typography variant="caption">0%</Typography>
              <Typography variant="caption">50%</Typography>
              <Typography variant="caption">100%</Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
};

export default ResultDisplay; 