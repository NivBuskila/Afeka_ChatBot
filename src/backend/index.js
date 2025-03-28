require('dotenv').config();
const express = require('express');
const cors = require('cors');
const { createClient } = require('@supabase/supabase-js');
const axios = require('axios');

const app = express();
const port = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());

// Supabase client initialization
const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'backend' });
});

// AI service integration
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }
    
    // Call AI service
    const aiResponse = await axios.post(`${process.env.AI_SERVICE_URL}/analyze`, {
      text: message
    });
    
    // Store in Supabase
    const { data, error } = await supabase
      .from('conversations')
      .insert([{ 
        message, 
        response: aiResponse.data,
        created_at: new Date()
      }]);
      
    if (error) throw error;
    
    return res.json(aiResponse.data);
  } catch (error) {
    console.error('Error processing chat:', error);
    return res.status(500).json({ error: 'Failed to process request' });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Backend server running on port ${port}`);
}); 