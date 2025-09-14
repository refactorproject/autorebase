import { z } from 'zod';

// AutoRebase request schema
export const AutoRebaseRequestSchema = z.object({
  base_software_0: z.string().min(3).max(100).describe('Base software 0 SHA or tag (e.g., "abc123" or "base/v1.0.0")'),
  base_software_1: z.string().min(3).max(100).describe('Base software 1 SHA or tag (e.g., "abc123" or "base/v1.0.1")'),
  feature_software_0: z.string().min(3).max(100).describe('Feature software 0 SHA or tag (e.g., "abc123" or "feature/v5.0.0")'),
  base_repo_url: z.string().url().describe('Base repository URL (used for base_software_0 and base_software_1)'),
  feature_repo_url: z.string().url().describe('Feature repository URL (used for feature_software_0)'),
  base_branch: z.string().optional().default('feature/v5.0.0').describe('Target branch for PR creation'),
  output_branch: z.string().optional().default('feature/v5.0.1').describe('New branch to create'),
  github_token: z.string().optional().describe('GitHub personal access token for authentication (optional, can also use GITHUB_TOKEN env var)')
});

export type AutoRebaseRequest = z.infer<typeof AutoRebaseRequestSchema>;

// AutoRebase response schema
export const AutoRebaseResponseSchema = z.object({
  success: z.boolean().describe('Whether the AutoRebase process was successful'),
  message: z.string().describe('Response message'),
  base_software_0: z.string().describe('Processed Base Software 0 SHA/tag'),
  base_software_1: z.string().describe('Processed Base Software 1 SHA/tag'),
  feature_software_0: z.string().describe('Processed Feature Software 0 SHA/tag'),
  base_repo_url: z.string().describe('Base repository URL used'),
  feature_repo_url: z.string().describe('Feature repository URL used'),
  resolved_files: z.array(z.object({
    path: z.string().describe('File path relative to repository root'),
    content: z.string().describe('Resolved file content'),
    conflict_resolved: z.boolean().describe('Whether this file had conflicts that were resolved'),
    ai_resolution_used: z.boolean().describe('Whether AI was used to resolve conflicts')
  })).optional().describe('Resolved files with their content'),
  processing_details: z.object({
    clone_results: z.object({
      success: z.boolean(),
      message: z.string(),
      results: z.record(z.object({
        success: z.boolean(),
        message: z.string(),
        directory: z.string(),
        sha: z.string()
      }))
    }),
    autorebase_results: z.object({
      success: z.boolean(),
      message: z.string(),
      details: z.object({
        files_processed: z.number(),
        patches_generated: z.number(),
        conflicts_resolved: z.number(),
        ai_resolutions: z.number()
      })
    })
  }).optional().describe('Detailed processing information')
});

export type AutoRebaseResponse = z.infer<typeof AutoRebaseResponseSchema>;

// Repository validation schema
export const ValidateRepositorySchema = z.object({
  repo_url: z.string().url().describe('Repository URL to validate'),
  sha_or_tag: z.string().min(3).max(100).describe('SHA or tag to validate')
});

export type ValidateRepositoryRequest = z.infer<typeof ValidateRepositorySchema>;

export const ValidateRepositoryResponseSchema = z.object({
  valid: z.boolean().describe('Whether the repository and SHA/tag are valid'),
  message: z.string().describe('Validation message'),
  sha: z.string().optional().describe('Resolved SHA if valid'),
  commit_message: z.string().optional().describe('Commit message if valid'),
  author: z.string().optional().describe('Author name if valid'),
  date: z.string().optional().describe('Commit date if valid')
});

export type ValidateRepositoryResponse = z.infer<typeof ValidateRepositoryResponseSchema>;
