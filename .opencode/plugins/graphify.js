// graphify OpenCode plugin
// Injects a one-time knowledge graph reminder before the first command.
import { existsSync } from "fs";
import { join } from "path";

export const GraphifyPlugin = async ({ directory }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (globalThis.__clakettesGraphifyReminded) return;
      if (!existsSync(join(directory, "graphify-out", "graph.json"))) return;
      if (input.tool !== "bash" && input.tool !== "shell") return;

      globalThis.__clakettesGraphifyReminded = true;
      const reminder =
        "echo '[graphify] knowledge graph available at graphify-out/. For focused questions use: graphify query <question> (scoped subgraph). Read GRAPH_REPORT.md only for broad architecture context.' ; ";
      output.args.command = reminder + output.args.command;
    },
  };
};
