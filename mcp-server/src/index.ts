#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { SSEServerTransport } from '@modelcontextprotocol/sdk/server/sse.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { AutoRebaseTools } from './tools.js';
import { createServer } from 'http';

/**
 * AutoRebase MCP Server
 * 
 * Provides tools for running AutoRebase with AI conflict resolution
 * on public GitHub repositories.
 */
class AutoRebaseMCPServer {
  private server: Server;
  private tools: AutoRebaseTools;
  private httpServer?: any;

  constructor() {
    this.server = new Server(
      {
        name: 'autorebase-mcp-server',
        version: '1.0.0',
      },
    );

    this.tools = new AutoRebaseTools();
    this.setupHandlers();
  }

  private setupHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: this.tools.getTools(),
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        const result = await this.tools.executeTool(name, args);
        return result;
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing tool ${name}: ${error instanceof Error ? error.message : 'Unknown error'}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run() {
    const transportMode = process.env.MCP_TRANSPORT || 'stdio';
    const port = parseInt(process.env.MCP_PORT || '3000');

    if (transportMode === 'http') {
      await this.runHttp(port);
    } else {
      await this.runStdio();
    }
  }

  private async runStdio() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('AutoRebase MCP Server running on stdio');
  }

  private async runHttp(port: number) {
    this.httpServer = createServer(async (req, res) => {
      // Handle CORS
      res.setHeader('Access-Control-Allow-Origin', '*');
      res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

      if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
      }

      // Health check endpoint
      if (req.url === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          status: 'healthy', 
          service: 'AutoRebase MCP Server',
          transport: 'http',
          port: port
        }));
        return;
      }

      // SSE endpoint for MCP communication
      if (req.url === '/message') {
        if (req.method === 'GET') {
          // SSE connection - let SSE transport handle headers
          const transport = new SSEServerTransport('/message', res);
          await this.server.connect(transport);
          return;
        } else if (req.method === 'POST') {
          // Handle POST messages
          let body = '';
          req.on('data', chunk => {
            body += chunk.toString();
          });
          
          req.on('end', async () => {
            try {
              const message = JSON.parse(body);
              // Process the message through the server
              res.writeHead(200, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ received: true }));
            } catch (error) {
              res.writeHead(400, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ error: 'Invalid JSON' }));
            }
          });
          return;
        }
      }

      // Default response
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not found' }));
    });

    this.httpServer.listen(port, () => {
      console.error(`AutoRebase MCP Server running on HTTP port ${port}`);
      console.error(`SSE endpoint: http://localhost:${port}/message`);
      console.error(`Health check: http://localhost:${port}/health`);
    });

    // Graceful shutdown
    process.on('SIGINT', () => {
      console.error('Shutting down HTTP server...');
      this.httpServer?.close();
      process.exit(0);
    });

    process.on('SIGTERM', () => {
      console.error('Shutting down HTTP server...');
      this.httpServer?.close();
      process.exit(0);
    });
  }
}

// Start the server
const server = new AutoRebaseMCPServer();
server.run().catch((error) => {
  console.error('Failed to start MCP server:', error);
  process.exit(1);
});