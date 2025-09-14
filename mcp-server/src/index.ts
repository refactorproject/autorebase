#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { AutoRebaseTools } from './tools.js';

/**
 * AutoRebase MCP Server
 * 
 * Provides tools for running AutoRebase with AI conflict resolution
 * on public GitHub repositories.
 */
class AutoRebaseMCPServer {
  private server: Server;
  private tools: AutoRebaseTools;

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
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('AutoRebase MCP Server running on stdio');
  }
}

// Start the server
const server = new AutoRebaseMCPServer();
server.run().catch((error) => {
  console.error('Failed to start MCP server:', error);
  process.exit(1);
});