const { Modal, Notice, Plugin, Setting } = require("obsidian");
const { execFile } = require("child_process");
const { promisify } = require("util");

const execFileAsync = promisify(execFile);

class CommitMessageModal extends Modal {
  constructor(app, onSubmit) {
    super(app);
    this.onSubmit = onSubmit;
    this.message = "Update vault";
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.createEl("h2", { text: "Commit and push vault" });

    new Setting(contentEl)
      .setName("Commit message")
      .addText((text) => {
        text
          .setPlaceholder("Describe your changes")
          .setValue(this.message)
          .onChange((value) => {
            this.message = value.trim();
          });
        text.inputEl.addEventListener("keydown", (event) => {
          if (event.key === "Enter" && this.message) {
            event.preventDefault();
            this.close();
            this.onSubmit(this.message);
          }
        });
        window.setTimeout(() => {
          text.inputEl.focus();
          text.inputEl.select();
        });
      });

    new Setting(contentEl)
      .addButton((button) =>
        button
          .setButtonText("Commit and push")
          .setCta()
          .onClick(() => {
            if (!this.message) {
              new Notice("Enter a commit message.");
              return;
            }
            this.close();
            this.onSubmit(this.message);
          })
      );
  }

  onClose() {
    this.contentEl.empty();
  }
}

module.exports = class VaultGitPlugin extends Plugin {
  async onload() {
    this.addCommand({
      id: "commit-and-push",
      name: "Commit and push",
      callback: () => {
        new CommitMessageModal(this.app, (message) =>
          this.commitAndPush(message)
        ).open();
      }
    });

    this.addCommand({
      id: "pull",
      name: "Pull",
      callback: () => this.pull()
    });
  }

  getVaultPath() {
    const adapter = this.app.vault.adapter;
    if (typeof adapter.getBasePath !== "function") {
      throw new Error("Vault Git requires a local desktop vault.");
    }
    return adapter.getBasePath();
  }

  async git(args) {
    return execFileAsync("git", args, {
      cwd: this.getVaultPath(),
      windowsHide: true,
      maxBuffer: 10 * 1024 * 1024
    });
  }

  formatError(error) {
    return (error.stderr || error.stdout || error.message || String(error)).trim();
  }

  async commitAndPush(message) {
    const notice = new Notice("Vault Git: committing and pushing…", 0);
    try {
      await this.git(["add", "--all"]);
      const { stdout: status } = await this.git(["status", "--porcelain"]);

      if (!status.trim()) {
        notice.hide();
        new Notice("Vault Git: no changes to commit.");
        return;
      }

      await this.git(["commit", "-m", message]);
      await this.git(["push"]);
      notice.hide();
      new Notice("Vault Git: committed and pushed successfully.", 5000);
    } catch (error) {
      notice.hide();
      console.error("Vault Git commit-and-push failed", error);
      new Notice(`Vault Git failed: ${this.formatError(error)}`, 10000);
    }
  }

  async pull() {
    const notice = new Notice("Vault Git: pulling…", 0);
    try {
      const { stdout } = await this.git(["pull", "--ff-only"]);
      notice.hide();
      const result = stdout.trim() || "Already up to date.";
      new Notice(`Vault Git: ${result}`, 5000);
    } catch (error) {
      notice.hide();
      console.error("Vault Git pull failed", error);
      new Notice(`Vault Git failed: ${this.formatError(error)}`, 10000);
    }
  }
};
