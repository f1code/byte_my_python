Title: Neovim TypeScript LSP Setup
Date: 2026-07-13
Modified: 2026-07-13
Category: Tools
Tags: neovim, typescript, lsp, developer-tools

LSP is the technology that allows Neovim (and many other editor) to provide code completion, navigation, and contextual
help.  How it works is a server process that knows all the specifics of the language and is able to examine the files, 
and a protocol (LSP) which lets the editor communicate with that server the same way for all languages.
LSP support is built in to Neovim, but you still have to enable and configure individual languages.
The `nvim-lspconfig` package bridges the gap and includes default configuration for many languages.

## What is special about TypeScript

TypeScript is a little different from other languages in that the standard `tsserver` language server does not implement
the standard LSP (Language Server Protocol), but a variation of it (that actually predates LSP).  So it needs a thin
adapter to let the editor communicates with it as if it were a regular LSP server.
There are two main options:

- `typescript-tools` seemed really promising, but it does not seem to be actively maintained—the last commit was in
  2025
- `ts_ls` wraps `typescript-language-server`. It is more standard, but slower. For reasonably sized projects, it remains OK.

I was using `typescript-tools` until recently, but started running into some issues. When I noticed it was not maintained anymore, I decided to give the standard `ts_ls` configuration a try.

## Enable `ts_ls` in Neovim

I use [Lazy.nvim](https://github.com/folke/lazy.nvim), so the config looks like this:

```lua
return {
	{
		-- pre-packaged LSP configurations
		-- see https://github.com/neovim/nvim-lspconfig/tree/master/lsp
		"neovim/nvim-lspconfig",
		config = function()
			-- for typescript-language-server
			vim.lsp.enable('ts_ls')
		end
	}
}
```

This relies on the executable `typescript-language-server` being present in `PATH` **and** on the project having a TypeScript installation.

If you have a warning about `typescript-language-server` not found, you typically need to do:

```bash
npm install -g typescript-language-server
```

Note: if you use a Node version manager, this is going to be specific to the version activated for the current project. So you may have to install a copy for each Node version.

## Fixing a monorepo error

Beyond that, one common error I got with monorepos:

```text
vim.schedule callback: .../neovim/0.12.4/share/nvim/runtime/lua/vim/lsp/client.lua:582: RPC[Error] code_name = InternalError, message = "Request initialize failed with message: Could not find a valid TypeScript installation. Please ensure that the \"typescript\" dependency is installed in the workspace or that a valid `tsserver.path` is specified. Exiting."
```

This happens because the language server looks for the TypeScript installed **for this project**. But in a monorepo, it might not find the right root. For example, GradeBee has this structure:

```text
root
|
|-- pnpm-lock.yaml -> lock file for the workspace
|-- package.json -> workspace-level config, without TypeScript
+-- frontend
    |
    |-- package.json -> frontend dependencies, including TypeScript
    +-- tsconfig.json
```

The default `ts_ls` setup will detect the project root by finding the lock file—in this case, the root of the workspace—but TypeScript is not installed at that location.

There are two possible fixes:

- Change the repo root detection. But then it still will not work to edit TypeScript files other than the ones under `frontend`.
- Install TypeScript at the workspace level. It is a bit redundant, but it does make it clear that there is a tooling dependency on TypeScript.

I chose the latter option. Since I use pnpm, I can add it to the `catalog` key in `pnpm-workspace.yaml`:

```yaml
catalog:
  typescript: ~6.0.2
```

Then, in both the root and `frontend` `package.json`, under `devDependencies`:

```json
"typescript": "catalog:"
```

## Links and final words

This is the current state, but the tools continue to evolve. Typescript 7.0 just came out and the compiler was
rewritten in Go.  Likely,  Microsoft will follow this with an implementation of the LSP server in Go to
address both the speed, and the compatibility concerns, making packages like `typescript-language-server` redundant.

Some links:

 - [My neovim config](https://github.com/f1code/vimrc)
 - [typescript-language-server](https://github.com/typescript-language-server/typescript-language-server)
 - [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig/blob/master/lua/lspconfig/configs/ts_ls.lua)
 - [Neovim LSP Documentation](https://neovim.io/doc/user/lsp/)
 - [typescript-tools](https://github.com/pmizio/typescript-tools.nvim)
