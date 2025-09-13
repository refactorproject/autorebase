export type ToolCall = {
  name: string;
  args: Record<string, any>;
};

export const tools = {
  "auto_rebase.init": (args: Record<string, string>) => [
    "init",
    "--old-base",
    args.old_base,
    "--new-base",
    args.new_base,
    "--feature",
    args.feature,
    "--req-map",
    args.req_map,
    "--workdir",
    args.workdir,
  ],
  "auto_rebase.extract_feature": (args: Record<string, string>) => [
    "extract-feature",
    "--out",
    args.out,
  ],
  "auto_rebase.extract_base": (args: Record<string, string>) => [
    "extract-base",
    "--out",
    args.out,
  ],
  "auto_rebase.retarget": (args: Record<string, string>) => [
    "retarget",
    "--feature-patch",
    args.feature_patch,
    "--base-patch",
    args.base_patch,
    "--new-base",
    args.new_base,
    "--out",
    args.out,
  ],
  "auto_rebase.validate": (args: Record<string, string>) => [
    "validate",
    "--path",
    args.path,
    "--report",
    args.report,
  ],
  "auto_rebase.finalize": (args: Record<string, string>) => [
    "finalize",
    "--path",
    args.path,
    "--tag",
    args.tag,
    "--trace",
    args.trace,
  ],
};

