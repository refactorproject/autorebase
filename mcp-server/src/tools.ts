import { Tool } from '@modelcontextprotocol/sdk/types.js';
import { AutoRebaseRequestSchema, ValidateRepositorySchema } from './types.js';
import { PythonBridge } from './python-bridge.js';

/**
 * MCP Tools for AutoRebase functionality
 */
export class AutoRebaseTools {
  private pythonBridge: PythonBridge;

  constructor() {
    this.pythonBridge = new PythonBridge();
  }

  /**
   * Get all available tools
   */
  getTools(): Tool[] {
    return [
      {
        name: 'autorebase',
        description: 'Run complete AutoRebase process with AI conflict resolution on public GitHub repositories',
        inputSchema: {
          type: 'object',
          properties: {
            base_software_0: {
              type: 'string',
              description: 'Base software 0 SHA or tag (e.g., "abc123" or "base/v1.0.0")',
              minLength: 3,
              maxLength: 100
            },
            base_software_1: {
              type: 'string',
              description: 'Base software 1 SHA or tag (e.g., "abc123" or "base/v1.0.1")',
              minLength: 3,
              maxLength: 100
            },
            feature_software_0: {
              type: 'string',
              description: 'Feature software 0 SHA or tag (e.g., "abc123" or "feature/v5.0.0")',
              minLength: 3,
              maxLength: 100
            },
            base_repo_url: {
              type: 'string',
              format: 'uri',
              description: 'Base repository URL (used for base_software_0 and base_software_1)'
            },
            feature_repo_url: {
              type: 'string',
              format: 'uri',
              description: 'Feature repository URL (used for feature_software_0)'
            },
            base_branch: {
              type: 'string',
              description: 'Target branch for PR creation (optional, defaults to feature/v5.0.0)',
              default: 'feature/v5.0.0'
            },
            output_branch: {
              type: 'string',
              description: 'New branch to create (optional, defaults to feature/v5.0.1)',
              default: 'feature/v5.0.1'
            },
            github_token: {
              type: 'string',
              description: 'GitHub personal access token for authentication (optional, can also use GITHUB_TOKEN env var)',
              default: null
            },
            use_ssh: {
              type: 'boolean',
              description: 'Use SSH authentication instead of token (optional, can also use SSH_OVERRIDE=true env var)',
              default: false
            }
          },
          required: [
            'base_software_0',
            'base_software_1',
            'feature_software_0',
            'base_repo_url',
            'feature_repo_url'
          ]
        }
      },
      {
        name: 'validate_repository',
        description: 'Validate a GitHub repository and SHA/tag combination',
        inputSchema: {
          type: 'object',
          properties: {
            repo_url: {
              type: 'string',
              format: 'uri',
              description: 'Repository URL to validate'
            },
            sha_or_tag: {
              type: 'string',
              description: 'SHA or tag to validate',
              minLength: 3,
              maxLength: 100
            }
          },
          required: ['repo_url', 'sha_or_tag']
        }
      },
      {
        name: 'get_changelog',
        description: 'Get the latest AutoRebase changelog information',
        inputSchema: {
          type: 'object',
          properties: {
            changelog_path: {
              type: 'string',
              description: 'Path to changelog file (optional, defaults to latest)',
              default: null
            }
          },
          required: []
        }
      }
    ];
  }

  /**
   * Execute a tool by name
   */
  async executeTool(name: string, arguments_: any): Promise<any> {
    switch (name) {
      case 'autorebase':
        return await this.executeAutoRebase(arguments_);
      case 'validate_repository':
        return await this.executeValidateRepository(arguments_);
      case 'get_changelog':
        return await this.executeGetChangelog(arguments_);
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  /**
   * Execute AutoRebase tool
   */
  private async executeAutoRebase(args: any): Promise<any> {
    try {
      // Validate input
      const validatedArgs = AutoRebaseRequestSchema.parse(args);
      
      // Call Python AutoRebase service
      const result = await this.pythonBridge.callAutoRebase(validatedArgs);
      
      // Format response for MCP
      return {
        content: [
          {
            type: 'text',
            text: `# AutoRebase Results

## Status: ${result.success ? '✅ Success' : '❌ Failed'}

**Message**: ${result.message}

## Repository Information
- **Base Software 0**: ${result.base_software_0}
- **Base Software 1**: ${result.base_software_1}
- **Feature Software 0**: ${result.feature_software_0}
- **Base Repository**: ${result.base_repo_url}
- **Feature Repository**: ${result.feature_repo_url}
- **Authentication**: ${args.use_ssh ? 'SSH' : args.github_token ? 'GitHub Token provided' : 'Using local credentials'}

## Resolved Files
${result.resolved_files && result.resolved_files.length > 0 
  ? result.resolved_files.map(file => 
      `### ${file.path}
- **Conflicts Resolved**: ${file.conflict_resolved ? 'Yes' : 'No'}
- **AI Resolution Used**: ${file.ai_resolution_used ? 'Yes' : 'No'}
- **Content Length**: ${file.content.length} characters

\`\`\`
${file.content.substring(0, 500)}${file.content.length > 500 ? '...' : ''}
\`\`\`
`).join('\n')
  : 'No files were processed or resolved.'}

## Processing Details
${result.processing_details ? `
- **Clone Results**: ${result.processing_details.clone_results.success ? 'Success' : 'Failed'}
- **Files Processed**: ${result.processing_details.autorebase_results.details.files_processed}
- **Patches Generated**: ${result.processing_details.autorebase_results.details.patches_generated}
- **Conflicts Resolved**: ${result.processing_details.autorebase_results.details.conflicts_resolved}
- **AI Resolutions**: ${result.processing_details.autorebase_results.details.ai_resolutions}
` : 'No processing details available.'}

## Changelog Information
${(result as any).autorebase_results && (result as any).autorebase_results.details && (result as any).autorebase_results.details.changelog ? `
### Summary
- **Timestamp**: ${(result as any).autorebase_results.details.changelog.timestamp}
- **Files Processed**: ${(result as any).autorebase_results.details.changelog.files_processed.length}
- **Patches Generated**: ${(result as any).autorebase_results.details.changelog.patches_generated.length}
- **Patches Applied**: ${(result as any).autorebase_results.details.changelog.patches_applied.length}
- **F1 Files Created**: ${(result as any).autorebase_results.details.changelog.f1_files_created.length}
- **Backup Files**: ${(result as any).autorebase_results.details.changelog.backup_files.length}
- **Reject Files**: ${(result as any).autorebase_results.details.changelog.reject_files.length}
- **Three-Way Merges**: ${(result as any).autorebase_results.details.changelog.three_way_merges.length}

### Files Processed
${(result as any).autorebase_results.details.changelog.files_processed.map((file: string) => `- ${file}`).join('\n')}

### Successful Patches Applied
${(result as any).autorebase_results.details.changelog.patches_applied.map((patch: any) => 
  `- **${patch.file}** (${patch.patch_type}) - ${patch.timestamp}`
).join('\n')}

### AI Resolutions
${(result as any).autorebase_results.details.changelog.three_way_merges.filter((merge: any) => merge.status === 'success').map((merge: any) => 
  `- **${merge.target_file}** - ${merge.conflict_type} (Score: ${merge.validation_score})`
).join('\n')}

### Failed Resolutions
${(result as any).autorebase_results.details.changelog.three_way_merges.filter((merge: any) => merge.status !== 'success').map((merge: any) => 
  `- **${merge.target_file}** - ${merge.status}: ${merge.error}`
).join('\n')}

### Changelog File Location
📁 **Changelog saved to**: \`${(result as any).autorebase_results.details.changelog_path}\`
` : 'No changelog information available.'}

## Next Steps
${result.success 
  ? 'The AutoRebase process completed successfully. You can now review the resolved files and create a pull request manually if needed.'
  : 'The AutoRebase process encountered issues. Please check the error message and try again.'}
`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `# AutoRebase Error

❌ **Error**: ${error instanceof Error ? error.message : 'Unknown error occurred'}

Please check your input parameters and try again.`
          }
        ],
        isError: true
      };
    }
  }

  /**
   * Execute repository validation tool
   */
  private async executeValidateRepository(args: any): Promise<any> {
    try {
      // Validate input
      const validatedArgs = ValidateRepositorySchema.parse(args);
      
      // Call Python validation service
      const result = await this.pythonBridge.validateRepository(
        validatedArgs.repo_url,
        validatedArgs.sha_or_tag
      );
      
      // Format response for MCP
      return {
        content: [
          {
            type: 'text',
            text: `# Repository Validation Results

## Status: ${result.valid ? '✅ Valid' : '❌ Invalid'}

**Message**: ${result.message}

${result.valid ? `
## Commit Information
- **SHA**: ${result.sha || 'N/A'}
- **Message**: ${result.commit_message || 'N/A'}
- **Author**: ${result.author || 'N/A'}
- **Date**: ${result.date || 'N/A'}

The repository and SHA/tag combination is valid and ready for AutoRebase processing.
` : `
The repository or SHA/tag combination is invalid. Please check:
- Repository URL is correct and accessible
- SHA/tag exists in the repository
- Repository is a public GitHub repository
`}
`
          }
        ]
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `# Validation Error

❌ **Error**: ${error instanceof Error ? error.message : 'Unknown error occurred'}

Please check your input parameters and try again.`
          }
        ],
        isError: true
      };
    }
  }

  /**
   * Execute Get Changelog tool
   */
  private async executeGetChangelog(args: any): Promise<any> {
    try {
      const changelogPath = args.changelog_path || 'data/repos/autorebase_changelog.json';
      
      // Try to read the changelog file
      const fs = await import('fs/promises');
      const path = await import('path');
      
      try {
        const changelogContent = await fs.readFile(changelogPath, 'utf-8');
        const changelog = JSON.parse(changelogContent);
        
        return {
          content: [
            {
              type: 'text',
              text: `# AutoRebase Changelog

## Summary
- **Timestamp**: ${changelog.timestamp}
- **Files Processed**: ${changelog.files_processed.length}
- **Patches Generated**: ${changelog.patches_generated.length}
- **Patches Applied**: ${changelog.patches_applied.length}
- **F1 Files Created**: ${changelog.f1_files_created.length}
- **Backup Files**: ${changelog.backup_files.length}
- **Reject Files**: ${changelog.reject_files.length}
- **Three-Way Merges**: ${changelog.three_way_merges.length}

## Files Processed
${changelog.files_processed.map((file: string) => `- ${file}`).join('\n')}

## Successful Patches Applied
${changelog.patches_applied.map((patch: any) => 
  `- **${patch.file}** (${patch.patch_type}) - ${patch.timestamp}`
).join('\n')}

## AI Resolutions
${changelog.three_way_merges.filter((merge: any) => merge.status === 'success').map((merge: any) => 
  `- **${merge.target_file}** - ${merge.conflict_type} (Score: ${merge.validation_score})`
).join('\n')}

## Failed Resolutions
${changelog.three_way_merges.filter((merge: any) => merge.status !== 'success').map((merge: any) => 
  `- **${merge.target_file}** - ${merge.status}: ${merge.error}`
).join('\n')}

## Full Changelog JSON
\`\`\`json
${JSON.stringify(changelog, null, 2)}
\`\`\`

📁 **Changelog file**: \`${changelogPath}\`
`
            }
          ]
        };
      } catch (fileError) {
        return {
          content: [
            {
              type: 'text',
              text: `# Changelog Error

❌ **Error**: Could not read changelog file at \`${changelogPath}\`

**Possible reasons:**
- No AutoRebase process has been run yet
- File path is incorrect
- File permissions issue

**Try running an AutoRebase process first to generate the changelog.**
`
            }
          ],
          isError: true
        };
      }
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error reading changelog: ${error instanceof Error ? error.message : 'Unknown error'}`
          }
        ],
        isError: true
      };
    }
  }
}
