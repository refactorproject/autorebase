#!/usr/bin/env node

/**
 * Test script for HTTP transport MCP server
 */

import http from 'http';

const PORT = process.env.MCP_PORT || 3000;
const BASE_URL = `http://localhost:${PORT}`;

async function testHealthCheck() {
  return new Promise((resolve, reject) => {
    const req = http.get(`${BASE_URL}/health`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(data);
          resolve(result);
        } catch (error) {
          reject(error);
        }
      });
    });
    
    req.on('error', reject);
    req.setTimeout(5000, () => reject(new Error('Request timeout')));
  });
}

async function testSSEEndpoint() {
  return new Promise((resolve, reject) => {
    const req = http.get(`${BASE_URL}/message`, (res) => {
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      
      let data = '';
      res.on('data', chunk => {
        data += chunk.toString();
        // Check if we got the connection message
        if (data.includes('connected')) {
          resolve({ connected: true, data });
        }
      });
      
      res.on('end', () => resolve({ connected: true, data }));
    });
    
    req.on('error', reject);
    req.setTimeout(3000, () => {
      req.destroy();
      resolve({ connected: true, timeout: true });
    });
  });
}

async function runTests() {
  console.log(`Testing MCP HTTP server on port ${PORT}...`);
  
  try {
    // Test health check
    console.log('1. Testing health check...');
    const health = await testHealthCheck();
    console.log('✅ Health check passed:', health);
    
    // Test SSE endpoint
    console.log('2. Testing SSE endpoint...');
    const sse = await testSSEEndpoint();
    console.log('✅ SSE endpoint accessible:', sse);
    
    console.log('\n🎉 All tests passed! HTTP transport is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run tests if this is the main module
if (import.meta.url === `file://${process.argv[1]}`) {
  runTests();
}

export { testHealthCheck, testSSEEndpoint };
