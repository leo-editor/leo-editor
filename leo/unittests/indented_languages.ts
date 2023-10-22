//@+leo-ver=5-thin
//@+node:ekr.20230917150336.1: * @file ../unittests/indented_languages.ts
// A test file for the indented_languages plugin.
// The typescript tests are based on files from leoJS.

//@+<< imports: indented_typescript_test.ts >>
//@+node:ekr.20230917150336.2: ** << imports: indented_typescript_test.ts >>
// Imports from leoApp.ts.
import * as vscode from 'vscode';
import * as g from './leoGlobals';
import * as utils from '../utils';
import { LeoGui, NullGui } from './leoGui';
import { NodeIndices, VNode, Position } from './leoNodes';
//@-<< imports: indented_typescript_test.ts >>
//@+others
//@+node:ekr.20230917152222.1: ** From vs-code side
//@+node:ekr.20230917151018.1: *3* From config.ts (condensed)
//@+node:ekr.20230917151018.2: *4* class Config
/**
 * * Configuration Settings Service
 */
export class Config implements ConfigMembers {

    // Config settings used on Leo's side
    public defaultReloadIgnore: string = Constants.CONFIG_DEFAULTS.DEFAULT_RELOAD_IGNORE;

    // Config settings used on vscode's side
    public leoTreeBrowse: boolean = Constants.CONFIG_DEFAULTS.LEO_TREE_BROWSE; // Used as Context Flag
    public leoID: string = Constants.CONFIG_DEFAULTS.LEO_ID;

    public setLeoJsSettingsPromise: Promise<unknown> = Promise.resolve();
    private _isBusySettingConfig: boolean = false;

    constructor(
        private _context: vscode.ExtensionContext,
        private _leoUI: LeoUI
    ) { }

    //@+others
    //@+node:ekr.20230917151018.4: *5* getFontConfig
    /**
     * * Get config from vscode for the UI font sizes
     * @returns the font settings object (zoom level and editor font size)
     */
    public getFontConfig(): FontSettings {
        let w_zoomLevel = vscode.workspace.getConfiguration(
            "window"
        ).get("zoomLevel");

        const w_config: FontSettings = {
            zoomLevel: Number(w_zoomLevel),
            fontSize: Number(w_fontSize)
        };

        return w_config;
    }

    //@+node:ekr.20230917151018.5: *5* setLeojsSettings
    /**
     * * Apply changes to the expansion config settings and save them in user settings.
     * @param p_changes is an array of codes and values to be changed
     * @returns a promise that resolves upon completion
     */
    public setLeojsSettings(p_changes: ConfigSetting[]): Promise<unknown> {
        this._isBusySettingConfig = true;
        const w_promises: Thenable<void>[] = [];
        const w_vscodeConfig = vscode.workspace.getConfiguration(Constants.CONFIG_NAME);
        p_changes.forEach(i_change => {
            // tslint:disable-next-line: strict-comparisons
            if (w_vscodeConfig.inspect(i_change.code)!.defaultValue === i_change.value) {
                // Set as undefined - same as default
                w_promises.push(w_vscodeConfig.update(i_change.code, undefined, true));
            } else {
                // Set as value which is not default
                w_promises.push(w_vscodeConfig.update(i_change.code, i_change.value, true));
            }
        });

        this.setLeoJsSettingsPromise = Promise.all(w_promises);
        return this.setLeoJsSettingsPromise.then(() => {
            this._isBusySettingConfig = false;
            this.buildFromSavedSettings();
            return Promise.resolve();
        });

    }

    //@+node:ekr.20230917151018.6: *5* setFontConfig
    /**
     * * Apply changes in font size settings and save them in user settings.
     */
    public setFontConfig(p_settings: FontSettings): void {
        if (p_settings.zoomLevel || p_settings.zoomLevel === 0) {
            if (!isNaN(p_settings.zoomLevel) && p_settings.zoomLevel <= 12 && p_settings.zoomLevel >= -12) {
                void vscode.workspace.getConfiguration("window")
                    .update("zoomLevel", p_settings.zoomLevel, true);
            } else {
                void vscode.window.showInformationMessage(
                    Constants.USER_MESSAGES.ZOOM_LEVEL_RANGE_LIMIT
                );
            }
        }
        if (p_settings.fontSize) {
            if (!isNaN(p_settings.fontSize) && p_settings.fontSize <= 30 && p_settings.fontSize >= 6) {
                void vscode.workspace.getConfiguration("editor")
                    .update("fontSize", p_settings.fontSize, true);
            } else {
                void vscode.window.showInformationMessage(
                    Constants.USER_MESSAGES.FONT_SIZE_RANGE_LIMIT
                );
            }
        }
    }

    //@+node:ekr.20230917151018.7: *5* setEnablePreview
    /**
     * * Set the workbench.editor.enablePreview vscode setting
     */
    public setEnablePreview(): Thenable<void> {
        return vscode.workspace.getConfiguration("workbench.editor")
            .update("enablePreview", true, true);
    }

    //@+node:ekr.20230917151018.10: *5* checkCloseEmptyGroups
    /**
     * * Check if the 'workbench.editor.closeEmptyGroups' setting is false
     * @param p_forced Forces the setting instead of just suggesting with a message
     */
    public checkCloseEmptyGroups(p_forced?: boolean): void {
        let w_result: any = false;
        const w_setting = vscode.workspace.getConfiguration("workbench.editor");
        if (w_setting.inspect("closeEmptyGroups")!.globalValue === undefined) {
            w_result = w_setting.inspect("closeEmptyGroups")!.defaultValue;
        } else {
            w_result = w_setting.inspect("closeEmptyGroups")!.globalValue;
        }
        if (w_result === true) {
            if (p_forced) {
                void this.clearCloseEmptyGroups();
                void vscode.window.showInformationMessage(Constants.USER_MESSAGES.CLOSE_EMPTY_CLEARED);
            } else {
                void vscode.window.showWarningMessage(
                    Constants.USER_MESSAGES.CLOSE_EMPTY_RECOMMEND,
                    Constants.USER_MESSAGES.FIX_IT
                ).then(p_chosenButton => {
                    if (p_chosenButton === Constants.USER_MESSAGES.FIX_IT) {
                        void vscode.commands.executeCommand(Constants.COMMANDS.CLEAR_CLOSE_EMPTY_GROUPS);
                    }
                });
            }
        }
    }

    //@-others
}
//@+node:ekr.20230917151106.1: *3* From extension.ts (condensed)
//@+node:ekr.20230917151106.2: *4* activate
/**
 * Entry point for Leo in Javascript.
 */
export async function activate(p_context: vscode.ExtensionContext) {

    if (p_context.extensionUri) {
        console.log('STARTUP: context.extensionUri: ', p_context.extensionUri.fsPath, p_context.extensionUri.scheme, p_context.extensionUri.toJSON(),);
    }

    // * Show a welcome screen on version updates, then start the actual extension.
    void showWelcomeIfNewer(w_leojsVersion, w_previousVersion)
        .then(() => {
            void p_context.globalState.update(Constants.VERSION_STATE_KEY, w_leojsVersion);
        });

    if (!g.app) {
        (g.app as LeoApp) = new LeoApp();
        (g.app as LeoApp).vscodeExtensionDir = p_context.extensionUri.fsPath;

        const gitExtension = vscode.extensions.getExtension<GitAPI.GitExtension>('vscode.git');
        if (gitExtension) {
            await gitExtension.activate();
            try {
                (g.gitAPI as GitAPI.API) = gitExtension.exports.getAPI(1);
                console.log("STARTUP:          GIT extension installed as g.gitAPI");

            } catch (e) {
                console.log("LEOJS ERROR : GIT EXTENSION NOT INSTALLED !");
            }
        } else {
            // console.log("LEOJS ERROR : GIT EXTENSION NOT AVAILABLE !");
        }

        const gitBaseExtension = vscode.extensions.getExtension<GitBaseAPI.GitBaseExtension>('vscode.git-base');
        if (gitBaseExtension) {
            await gitBaseExtension.activate();
            try {
                (g.gitBaseAPI as GitBaseAPI.API) = gitBaseExtension.exports.getAPI(1);
                console.log("STARTUP:          GIT_BASE extension installed as g.gitBaseAPI");
            } catch (e) {
                console.log("LEOJS ERROR : GIT_BASE EXTENSION NOT INSTALLED !");
            }
        } else {
            // console.log("LEOJS ERROR : GIT_BASE EXTENSION NOT AVAILABLE !");
        }

        SQL = await initSqlJs(undefined, sqliteBits);
        console.log("STARTUP:          SQLITE has started");
        (g.SQL as SqlJsStatic) = SQL;

    } else {
        void vscode.window.showWarningMessage("g.app leojs application instance already exists!");
    }

    async function dbTests() {

        const filebuffer = await vscode.workspace.fs.readFile(
            g.makeVscodeUri(path.join(vscode.workspace.workspaceFolders![0].uri.fsPath, "test2.db"))
        );
        console.log('Done with DB tests');

    }

    async function readZipTest() {
        console.log('Starting readZipTest');
        try {
            w_stats = await vscode.workspace.fs.stat(w_uri);
        } catch {
            return false;
        }
        console.log('w_stats.size', w_stats.size);

        await vscode.workspace.fs.readFile(w_uri)
            .then(JSZip.loadAsync)                            // 3) chain with the zip promise
            .then(function (zip) {
                return zip.file("hello.txt")?.async("string"); // 4) chain with the text content promise
            })
            .then((read_str) => {
                console.log('read from zip hello.txt: ', read_str);
            });
        console.log('Done with readZipTest');
    }

    async function makeZipTest() {
        console.log('Starting makeZipTest');
    }

    if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length) {
        console.log('GOT WORKSPACE: starting file-system ZIP & DB tests');
        if (0) {
            await dbTests();
        }
        if (0) {
            await readZipTest();
        } else if (0) {
            await makeZipTest();
        }
    }

    if (!g.isBrowser) {
        // Regular NodeJs Extension: Dont wait for workspace being opened
        if (!g.app.vscodeUriScheme) {
            // Only setting if undefined, because regular vscode can still work on remote github virtual filesystem
            g.app.vscodeUriScheme = 'file';
        }
        await runLeo(p_context);
    } else {
        // Web Browser Extension: CHeck for type of workspace opened first
        if (g.app.vscodeUriScheme) {

            if (!vscode.workspace.fs.isWritableFileSystem(g.app.vscodeUriScheme)) {
                void vscode.window.showInformationMessage("Non-writable filesystem scheme: " + g.app.vscodeUriScheme, "More Info")
                    .then(selection => {
                        if (selection === "More Info") {
                            vscode.env.openExternal(
                                vscode.Uri.parse('https://code.visualstudio.com/docs/editor/vscode-web#_current-limitations')
                            ).then(() => { }, (e) => {
                                console.error('LEOJS: Could not open external vscode help URL in browser.', e);
                            });
                        }
                    });
                console.log('NOT started because not writable workspace');
                void setStartupDoneContext(true);
                return;
            }

            // Check if not file scheme : only virtual workspaces are suported if g.isBrowser is true.
            if (g.app.vscodeUriScheme !== 'file') {
                console.log('STARTUP: g.app.vscodeWorkspaceUri: ', g.app.vscodeWorkspaceUri);
            } else {
                // Is local filesystem
                void vscode.window.showInformationMessage("LeoJS in browser supports remote virtual filesystems: Local Filesystem requires desktop VSCode application: ", "More Info").then(selection => {
                    if (selection === "More Info") {
                        vscode.env.openExternal(
                            vscode.Uri.parse('https://code.visualstudio.com/docs/editor/vscode-web#_opening-a-project')
                        ).then(() => { }, (e) => {
                            console.error('LEOJS: Could not open external vscode help URL in browser.', e);
                        });
                    }
                });
                console.log('NOT started because no remote workspace yet');
                void setStartupDoneContext(true);
                return;
            }
        } else {
            console.log('NOT started because no remote workspace yet');
            void setStartupDoneContext(true);
        }

    }

}

//@+node:ekr.20230917151106.7: *4* closeLeoTextEditors
/**
 * * Closes all visible text editors that have Leo filesystem scheme (that are not dirty)
 */
async function closeLeoTextEditors(): Promise<unknown> {
    const w_foundTabs: vscode.Tab[] = [];

    vscode.window.tabGroups.all.forEach((p_tabGroup) => {
        p_tabGroup.tabs.forEach((p_tab) => {

            if (p_tab.input &&
                (p_tab.input as vscode.TabInputText).uri &&
                (p_tab.input as vscode.TabInputText).uri.scheme === Constants.URI_LEO_SCHEME &&
                !p_tab.isDirty

            ) {
                w_foundTabs.push(p_tab);
            }
        });
    });

    let q_closedTabs;
    if (w_foundTabs.length) {
        q_closedTabs = vscode.window.tabGroups.close(w_foundTabs, true);
        for (const p_tab of w_foundTabs) {
            if (p_tab.input) {
                await vscode.commands.executeCommand(
                    'vscode.removeFromRecentlyOpened',
                    (p_tab.input as vscode.TabInputText).uri
                );
                // Delete to close all other body tabs.
                // (w_oldUri will be deleted last below)
                const w_edit = new vscode.WorkspaceEdit();
                w_edit.deleteFile((p_tab.input as vscode.TabInputText).uri, { ignoreIfNotExists: true });
                await vscode.workspace.applyEdit(w_edit);
            }
        }
    } else {
        q_closedTabs = Promise.resolve(true);
    }
    return q_closedTabs;
}

//@+node:ekr.20230917151106.8: *4* showWelcomeIfNewer
/**
 * * Show welcome screen if needed, based on last version executed
 * @param p_version Current version, as a string, from packageJSON.version
 * @param p_previousVersion Previous version, as a string, from context.globalState.get service
 * @returns A promise that triggers when command to show the welcome screen is finished, or immediately if not needed
 */
function showWelcomeIfNewer(p_version: string, p_previousVersion: string | undefined): Thenable<unknown> {
    let w_showWelcomeScreen: boolean = false;
    if (p_previousVersion === undefined) {
        console.log('leojs first-time install');
        w_showWelcomeScreen = true;
    } else {
        if (p_previousVersion !== p_version) {
            void vscode.window.showInformationMessage(`leojs upgraded from v${p_previousVersion} to v${p_version}`);
        }
        const [w_major, w_minor] = p_version.split('.').map(p_stringVal => parseInt(p_stringVal, 10));
        const [w_prevMajor, w_prevMinor] = p_previousVersion.split('.').map(p_stringVal => parseInt(p_stringVal, 10));
        if (
            (w_major === w_prevMajor && w_minor === w_prevMinor) ||
            // Don't notify on downgrades
            (w_major < w_prevMajor || (w_major === w_prevMajor && w_minor < w_prevMinor))
        ) {
            w_showWelcomeScreen = false;
        } else if (w_major !== w_prevMajor || (w_major === w_prevMajor && w_minor > w_prevMinor)) {
            // Will show on major or minor upgrade (Formatted as 'Major.Minor.Revision' eg. 1.2.3)
            w_showWelcomeScreen = true;
        }
    }
    if (w_showWelcomeScreen) {
        return vscode.commands.executeCommand(Constants.COMMANDS.SHOW_WELCOME);
    } else {
        return Promise.resolve();
    }
}

//@+node:ekr.20230917152233.1: ** From Leo side
//@+node:ekr.20230917150958.1: *3* From leoApp.ts (condensed)
//@+node:ekr.20230917150336.3: *4* class IdleTimeManager
/**
 *  A singleton class to manage idle-time handling.
 */
export class IdleTimeManager {
    on_idle_count = 0;

    constructor() {
        this.callback_list = [];
        this.timer = null;
    }

    //@+others
    //@+node:ekr.20230917150336.5: *5* itm.on_idle
    /**
     * IdleTimeManager: Run all idle-time callbacks.
     */
    public on_idle(timer: any): void {
        if (!g.app) {
            return;
        }
        if (g.app.killed) {
            return;
        }
        if (!g.app.pluginsController) {
            g.trace('No g.app.pluginsController', g.callers());
            timer.stop();
            return; // For debugger.
        }
        this.on_idle_count += 1;
        // Handle the registered callbacks.
        for (const callback of this.callback_list) {
            try {
                callback();
            } catch (exception) {
                g.es_exception(exception);
                g.es_print(`removing callback: ${callback.toString()}`);
                const index = this.callback_list.indexOf(callback);
                if (index > -1) {
                    // only splice array when item is found
                    this.callback_list.splice(index, 1); // 2nd parameter means remove one item only
                }
            }
        }
    }
    //@+node:ekr.20230917150336.6: *5* itm.start
    /**
     * Start the idle-time timer.
     */
    public start(): void {
        this.timer = g.IdleTime(
            this.on_idle.bind(this),
            1000, // 500, // ! ORIGINAL INTERVAL IS 500 !
            'IdleTimeManager.on_idle'
        );
        if (this.timer && this.timer.start) {
            this.timer.start(); // this.timer is a idleTimeClass, which can be a dummy object in unit-tests
        }
    }
    //@-others
}

//@+node:ekr.20230917150336.7: *4* class LeoApp
/**
 * A class representing the Leo application itself.
 * instance variables of this class are Leo's global variables.
 */
export class LeoApp {
    //@+others
    //@+node:ekr.20230917150336.8: *5* app.Birth & startup
    //@+node:ekr.20230917150336.9: *6* app.__init__ (helpers contain language dicts)
    //@+<< LeoApp: command-line arguments >>
    //@+node:ekr.20230917150336.10: *7* << LeoApp: command-line arguments >>
    // TODO : CHECK IF always_write_session_data IS NEEDED ! 
    public always_write_session_data: boolean = false;  // Default: write session data only if no files on command line.

    public batchMode: boolean = false; // True: run in batch mode.
    public debug: string[] = []; // A list of switches to be enabled.
    public diff: boolean = false; // True: run Leo in diff mode.
    public enablePlugins: boolean = true; // True: run start1 hook to load plugins. --no-plugins
    public failFast: boolean = false; // True: Use the failfast option in unit tests.
    public gui!: NullGui; // The gui class.
    public vscode: typeof vscode = vscode;
    public guiArgName: string | undefined; // The gui name given in --gui option.
    public listen_to_log_flag: boolean = false; // True: execute listen-to-log command.
    public loaded_session: boolean = false; // Set at startup if no files specified on command line.
    public silentMode: boolean = false; // True: no sign-on.
    public trace_binding: string | undefined; // The name of a binding to trace, or None.
    public trace_setting: string | undefined; // The name of a setting to trace, or None.
    public write_black_sentinels = false; // True: write a space befor '@' in sentinel lines.

    //@-<< LeoApp: command-line arguments >>
    //@+<< LeoApp: global directories >>
    //@+node:ekr.20230917150336.13: *7* << LeoApp: global directories >>
    public extensionsDir: string | undefined; // The leo / extensions directory
    public globalConfigDir: string | undefined; // leo / config directory
    public globalOpenDir: string | undefined; // The directory last used to open a file.
    public homeDir: string | undefined; // The user's home directory.
    public homeLeoDir: string | undefined; // The user's home/.leo directory.
    public testDir: string | undefined; // Used in unit tests
    public loadDir: string | undefined; // The leo / core directory.
    public vscodeExtensionDir: string | undefined;
    public machineDir: string | undefined; // The machine - specific directory.

    public vscodeWorkspaceUri: vscode.Uri | undefined;
    public vscodeUriAuthority: string = '';
    public vscodeUriPath: string = '';

    //@-<< LeoApp: global directories >>
    //@+<< LeoApp: global data >>
    //@+node:ekr.20230917150336.14: *7* << LeoApp: global data >>
    public atAutoNames: string[] = []; // The set of all @auto spellings.
    public atFileNames: string[] = []; // The set of all built -in @<file>spellings.

    public vscodeUriScheme: string = ''; // * VSCODE WORKSPACE FILE SCHEME
    public globalKillBuffer: any[] = []; // The global kill buffer.
    public globalRegisters: any = {}; // The global register list.
    public leoID: string = ''; // The id part of gnx's, using empty for falsy.
    public loadedThemes: any[] = []; // List of loaded theme.leo files.
    public lossage: any[] = []; // List of last 100 keystrokes.
    public paste_c: any = null; // The commander that pasted the last outline.
    public spellDict: any = null; // The singleton PyEnchant spell dict.
    public numberOfUntitledWindows: number = 0; // Number of opened untitled windows.
    public windowList: LeoFrame[] = []; // * Global list of all frames.
    public realMenuNameDict = {}; // Translations of menu names.

    //@-<< LeoApp: global data >>

    public delegate_language_dict: { [key: string]: string } = {};
    public extension_dict: { [key: string]: string } = {};
    public extra_extension_dict: { [key: string]: string } = {};
    public prolog_prefix_string: string = '';
    public prolog_postfix_string: string = '';
    public prolog_namespace_string: string = '';
    public language_delims_dict: { [key: string]: string } = {};
    public language_extension_dict: { [key: string]: string } = {};

    //@+others
    //@+node:ekr.20230917150336.24: *7* constructor
    constructor() {
        // Define all global data.
        this.init_at_auto_names();
        this.init_at_file_names();
    }

    //@+node:ekr.20230917150336.29: *7* app.define_language_extension_dict
    public define_language_extension_dict(): void {
        // Used only by g.app.externalFilesController.get_ext.

        // Keys are languages, values are extensions.
        this.language_extension_dict = {
            actionscript: 'as', // jason 2003-07 - 03
            xml: 'xml',
            xsl: 'xsl',
            xslt: 'xsl',
            yaml: 'yaml',
            zpt: 'zpt',
        };
    }

    //@+node:ekr.20230917150336.30: *7* app.init_at_auto_names
    /**
     * Init the app.atAutoNames set.
     */
    public init_at_auto_names(): void {
        this.atAutoNames = ['@auto-rst', '@auto'];
    }

    //@+node:ekr.20230917150336.31: *7* app.init_at_file_names
    /**
     * Init the app.atFileNames set.
     */
    public init_at_file_names(): void {
        this.atFileNames = [
            '@asis',
            '@edit',
            '@file-asis',
            '@file-thin',
            '@file-nosent',
            '@file',
            '@clean',
            '@nosent',
            '@shadow',
            '@thin',
        ];
    }

    //@-others

    //@+node:ekr.20230917150336.32: *6* app.computeSignon & printSignon
    public computeSignon(): void {
        const app = this;
        if (app.signon && app.signon1) {
            return;
        }

        let guiVersion = 'VSCode version ' + vscode.version;

        const w_LeoJSExtension = vscode.extensions.getExtension(
            Constants.PUBLISHER + '.' + Constants.NAME
        )!;
        const w_leojsPackageJson = w_LeoJSExtension.packageJSON;

        const leoVer: string = w_leojsPackageJson.version;

        // n1, n2, n3, junk1, junk2 = sys.version_info
        let n1: string = '';
        if (process.version) {
            n1 = 'Node.js ' + process.version;
            // // @ts-expect-error
        } else if (location.hostname) {
            // // @ts-expect-error
            n1 = location.hostname;
            // if dots take 2 last parts
            if (n1.includes('.')) {
                let n1_split = n1.split('.');
                if (n1_split.length > 2) {
                    n1_split = n1_split.slice(-2);
                }
                n1 = n1_split.join('.');
            }
        }
        if (n1) {
            n1 += ', ';
        }

        let sysVersion: string = 'Browser';

        if (process.platform) {
            sysVersion = process.platform;
        } else {
            let browserResult: any;
            // // @ts-expect-error
            if (navigator.userAgent) {
                // // @ts-expect-error
                browserResult = Bowser.parse(navigator.userAgent);
                sysVersion = browserResult.browser.name;
                if (browserResult.browser.version) {
                    sysVersion += ' ' + browserResult.browser.version;
                }

                if (browserResult.os) {
                    if (browserResult.os.name) {
                        sysVersion += ' on ' + browserResult.os.name;
                    }
                    if (browserResult.os.version) {
                        sysVersion += ' ' + browserResult.os.version;
                    }
                }
            }
        }
        // TODO: fleshout Windows info
        /*
        if sys.platform.startswith('win'):
            sysVersion = 'Windows '
            try:
                // peckj 20140416: determine true OS architecture
                // the following code should return the proper architecture
                // regardless of whether or not the python architecture matches
                // the OS architecture (i.e. python 32-bit on windows 64-bit will return 64-bit)
                v = platform.win32_ver()
                release, winbuild, sp, ptype = v
                true_platform = os.environ['PROCESSOR_ARCHITECTURE']
                try:
                    true_platform = os.environ['PROCESSOR_ARCHITEw6432']
                except KeyError:
                    pass
                sysVersion = f"Windows {release} {true_platform} (build {winbuild}) {sp}"
            except Exception:
                pass
        else: sysVersion = sys.platform 
        */

        // branch, junk_commit = g.gitInfo()
        const branch = w_leojsPackageJson.gitBranch;

        // author, commit, date = g.getGitVersion()
        const commit = w_leojsPackageJson.gitCommit;
        const date = w_leojsPackageJson.gitDate;

        // Compute g.app.signon.
        const signon: string[] = [`LeoJS ${leoVer}`];
        if (branch) {
            signon.push(`, ${branch} branch`);
        }
        if (commit) {
            signon.push(', build ' + commit);
        }
        if (date) {
            signon.push('\n' + date);
        }
        app.signon = signon.join('');
        // Compute g.app.signon1.
        app.signon1 = `${n1}${guiVersion}\n${sysVersion}`;
    }

    /**
     * Print the signon to the log.
     */
    public printSignon(): void {
        const app = this;

        if (app.silentMode) {
            return;
        }
        /*         
        if (sys.stdout.encoding && sys.stdout.encoding.lower() !== 'utf-8'){
            console.log('Note: sys.stdout.encoding is not UTF-8');
            console.log(`Encoding is: ${sys.stdout.encoding}`);
            console.log('See: https://stackoverflow.com/questions/14109024');
            console.log('');
        }
        */
        // * Modified for leojs SINGLE log pane
        g.es_print(app.signon);
        g.es_print(app.signon1);
    }
    //@+node:ekr.20230917150336.33: *6* app.setGlobalDb
    /**
     * Create global pickleshare db
     *
     * Usable by:
     *
     *    g.app.db['hello'] = [1,2,5]
     */
    public async setGlobalDb(): Promise<void> {

        // Fixes bug 670108.

        g.app.global_cacher = new GlobalCacher();
        await g.app.global_cacher.init();
        g.app.db = g.app.global_cacher.db;
        g.app.commander_cacher = new CommanderCacher();
        await g.app.commander_cacher.init();
        g.app.commander_db = g.app.commander_cacher.db;

    }
    //@+node:ekr.20230917150336.34: *6* app.setLeoID & helpers
    /**
     * Get g.app.leoID from various sources.
     */
    public async setLeoID(
        useDialog: boolean = true,
        verbose: boolean = true
    ): Promise<string> {
        this.leoID = '';

        // tslint:disable-next-line: strict-comparisons
        console.assert(this === g.app);

        verbose = verbose && !g.unitTesting && !this.silentMode;

        // if (g.unitTesting) {
        //     this.leoID = "unittestid";
        // }

        let w_userName = ''; // = "TestUserName";

        // 1 - set leoID from configuration settings
        if (!this.leoID && vscode && vscode.workspace) {
            w_userName = vscode.workspace
                .getConfiguration(Constants.CONFIG_NAME)
                .get(
                    Constants.CONFIG_NAMES.LEO_ID,
                    Constants.CONFIG_DEFAULTS.LEO_ID
                );
            if (w_userName) {
                this.leoID = this.cleanLeoID(w_userName, 'config.leoID');
            }
        }

        // 2 - Set leoID from environment
        if (!this.leoID && os && os.userInfo) {
            w_userName = os.userInfo().username;
            if (w_userName) {
                this.leoID = this.cleanLeoID(
                    w_userName,
                    'os.userInfo().username'
                );
            }
        }

        // 3 - Set leoID from user dialog if allowed
        if (!this.leoID && useDialog) {
            const w_id = await utils.getIdFromDialog();
            this.leoID = this.cleanLeoID(w_id, '');
            if (this.leoID && vscode && vscode.workspace) {
                const w_vscodeConfig = vscode.workspace.getConfiguration(
                    Constants.CONFIG_NAME
                );
                // tslint:disable-next-line: strict-comparisons
                if (
                    w_vscodeConfig.inspect(Constants.CONFIG_NAMES.LEO_ID)!
                        .defaultValue === this.leoID
                ) {
                    // Set as undefined - same as default
                    await w_vscodeConfig.update(
                        Constants.CONFIG_NAMES.LEO_ID,
                        undefined,
                        true
                    );
                } else {
                    // Set as value which is not default
                    await w_vscodeConfig.update(
                        Constants.CONFIG_NAMES.LEO_ID,
                        this.leoID,
                        true
                    );
                }
            }
        }
        if (!this.leoID) {
            // throw new Error("Could not get Leo ID");
            this.leoID = 'None';
        }
        return this.leoID;
    }

    //@+node:ekr.20230917150336.35: *7* app.cleanLeoID
    /**
     * #1404: Make sure that the given Leo ID will not corrupt a .leo file.
     */
    public cleanLeoID(id_: string, tag: string): string {
        const old_id: string = id_.toString();
        try {
            id_ = id_
                .replace(/\./g, '')
                .replace(/\,/g, '')
                .replace(/\"/g, '')
                .replace(/\'/g, '');
            //  Remove *all* whitespace: https://stackoverflow.com/questions/3739909
            id_ = id_.split(' ').join('');
        } catch (exception) {
            g.es_exception(exception);
            id_ = '';
        }
        if (id_.length < 3) {
            id_ = '';
            void vscode.window.showInformationMessage(
                `Invalid Leo ID: ${tag}`,
                {
                    detail:
                        `Invalid Leo ID: ${old_id}\n\n` +
                        'Your id should contain only letters and numbers\n' +
                        'and must be at least 3 characters in length.',
                    modal: true,
                }
            );
        }
        return id_;
    }

    //@+node:ekr.20230917150336.36: *5* app.Closing
    //@+node:ekr.20230917150336.37: *6* app.closeLeoWindow
    /**
     * Attempt to close a Leo window.
     */
    public async closeLeoWindow(
        frame: LeoFrame,
        new_c?: Commands,
        finish_quit = true
    ): Promise<boolean> {
        const c = frame.c;
        if (g.app.debug.includes('shutdown')) {
            g.trace(`changed: ${c.changed} ${c.shortFileName()}`);
        }
        c.endEditing(); // Commit any open edits.
        if (c.promptingForClose) {
            // There is already a dialog open asking what to do.
            return false;
        }

        // TODO : NEEDED ?
        // Make sure .leoRecentFiles.txt is written.
        // g.app.recentFilesManager.writeRecentFilesFile(c)

        if (c.changed) {
            c.promptingForClose = true;
            const veto = await frame.promptForSave();
            c.promptingForClose = false;
            if (veto) {
                return false;
            }
        }
        // g.app.setLog(None)  // no log until we reactive a window.

        g.doHook('close-frame', { c: c });
        //
        // Save the window state for *all* open files.
        if (g.app.commander_cacher) {
            await g.app.commander_cacher.commit(); // store cache, but don't close it.
        }
        // This may remove frame from the window list.
        if (g.app.windowList.includes(frame)) {
            await g.app.destroyWindow(frame);

            // Remove frame
            let index = g.app.windowList.indexOf(frame, 0);
            if (index > -1) {
                g.app.windowList.splice(index, 1);
            }
        } else {
            // #69.
            g.app.forgetOpenFile(c.fileName());
        }

        if (g.app.windowList.length) {
            const c2 = new_c || g.app.windowList[0].c;
            g.app.selectLeoWindow(c2);
        } else if (finish_quit && !g.unitTesting) {
            // * Does not terminate when last is closed: Present 'new' and 'open' buttons instead!
            // g.app.finishQuit();
        }
        return true; // The window has been closed.
    }
    //@+node:ekr.20230917150336.38: *6* app.destroyWindow
    /**
     * Destroy all ivars in a Leo frame.
     */
    public async destroyWindow(frame: LeoFrame): Promise<void> {
        if (g.app.debug.includes('shutdown')) {
            g.pr(`destroyWindow:  ${frame.c.shortFileName()}`);
        }
        if (
            g.app.externalFilesController &&
            g.app.externalFilesController.destroy_frame
        ) {
            await g.app.externalFilesController.destroy_frame(frame);
        }
        if (g.app.windowList.includes(frame)) {
            g.app.forgetOpenFile(frame.c.fileName());
        }
        // force the window to go away now.
        // Important: this also destroys all the objects of the commander.
        frame.destroySelf();
    }
    //@+node:ekr.20230917150336.39: *5* app.commanders
    /**
     * Return list of currently active controllers
     */
    public commanders(): Commands[] {
        return g.app.windowList.map((f) => f.c);
    }
    //@+node:ekr.20230917150336.40: *5* app.Detecting already-open files
    //@+node:ekr.20230917150336.41: *6* app.checkForOpenFile
    /**
     * Warn if fn is already open and add fn to already_open_files list.
     */
    public checkForOpenFile(c: Commands, fn: string): void {
        const d: any = g.app.db;
        const tag: string = 'open-leo-files';
        if (g.app.reverting) {
            // #302: revert to saved doesn't reset external file change monitoring
            g.app.already_open_files = [];
        }
        if (
            d === undefined ||
            g.unitTesting ||
            g.app.batchMode ||
            g.app.reverting ||
            g.app.inBridge
        ) {
            return;
        }
        console.log('TODO : checkForOpenFile');

        // #1519: check os.path.exists.
        /*
        const aList: string[] = g.app.db[tag] || [];  // A list of normalized file names.
        let w_any: boolean = false;
        for (let z of aList) {
            if (fs.existsSync(z) && z.toString().trim() === fn.toString().trim()) {
                w_any = true;
            }
        }
        // any(os.path.exists(z) and os.path.samefile(z, fn) for z in aList)
        if (w_any) {
            // The file may be open in another copy of Leo, or not:
            // another Leo may have been killed prematurely.
            // Put the file on the global list.
            // A dialog will warn the user such files later.
            fn = path.normalize(fn);
            if (!g.app.already_open_files.includes(fn)) {
                g.es('may be open in another Leo:', 'red');
                g.es(fn);
                g.app.already_open_files.push(fn);
            }

        } else {
            g.app.rememberOpenFile(fn);
        }
        */
        // TODO maybe
        // Temp fix
        g.app.rememberOpenFile(fn);
    }
    //@+node:ekr.20230917150336.42: *6* app.forgetOpenFile
    /**
     * Forget the open file, so that is no longer considered open.
     */
    public forgetOpenFile(fn: string): void {
        console.log('TODO : TEST forgetOpenFile');

        const trace: boolean = g.app.debug.includes('shutdown');
        const d: any = g.app.db;
        const tag: string = 'open-leo-files';

        if (!d || !fn) {
            return; // #69.
        }

        const aList: string[] = d[tag] || [];

        fn = path.normalize(fn);

        if (aList.includes(fn)) {
            // aList.remove(fn)
            const index = aList.indexOf(fn);
            if (index > -1) {
                aList.splice(index, 1);
            }

            if (trace) {
                g.pr(`forgetOpenFile: ${g.shortFileName(fn)}`);
            }
            d[tag] = aList;
        }
    }
    //@+node:ekr.20230917150336.43: *6* app.rememberOpenFile
    public rememberOpenFile(fn: string): void {
        console.log('TODO : TEST rememberOpenFile');

        // Do not call g.trace, etc. here.
        const d = g.app.db;
        const tag = 'open-leo-files';

        if (
            d === undefined ||
            g.unitTesting ||
            g.app.batchMode ||
            g.app.reverting
        ) {
            // pass
        } else if (g.app.preReadFlag) {
            // pass
        } else {
            const aList: string[] = d[tag] || [];
            // It's proper to add duplicates to this list.
            aList.push(path.normalize(fn));
            d[tag] = aList;
        }
    }
    //@+node:ekr.20230917150336.45: *5* app.Import utils
    //@+node:ekr.20230917150336.46: *6* app.scanner_for_at_auto
    /**
     * A factory returning a scanner function for p, an @auto node.
     */
    public scanner_for_at_auto(
        c: Commands,
        p: Position
    ): ((...args: any[]) => any) | undefined {
        const d = g.app.atAutoDict;
        for (const key in d) {
            // USING 'in' for KEYS

            const func = d[key];
            if (func && g.match_word(p.h, 0, key)) {
                return func;
            }
        }
        return undefined;
    }
    //@+node:ekr.20230917150336.47: *6* app.scanner_for_ext
    /**
     * A factory returning a scanner function for the given file extension.
     */
    public scanner_for_ext(
        c: Commands,
        ext: string
    ): ((...args: any[]) => any) | undefined {
        return g.app.classDispatchDict[ext];
    }
    //@+node:ekr.20230917150336.49: *5* app.newCommander
    /**
     * Create a commander and its view frame for the Leo main window.
     */
    public newCommander(
        fileName: string,
        gui?: LeoGui,
        previousSettings?: PreviousSettings,
        relativeFileName?: string
    ): Commands {
        // Create the commander and its subcommanders.
        // This takes about 3/4 sec when called by the leoBridge module.
        // Timeit reports 0.0175 sec when using a nullGui.
        if (!gui) {
            gui = g.app.gui;
        }
        const c = new Commands(
            fileName,
            gui,
            previousSettings,
            relativeFileName
        );
        return c;
    }
    //@-others
}

//@+node:ekr.20230917150336.51: *4* class LoadManager
/**
 * A class to manage loading .leo files, including configuration files.
 */
export class LoadManager {
    // Global settings & shortcuts dicts...
    // The are the defaults for computing settings and shortcuts for all loaded files.

    // A g.SettingsDict: the join of settings in leoSettings.leo & myLeoSettings.leo.
    public globalSettingsDict!: g.SettingsDict;
    // A g.SettingsDict: the join of shortcuts in leoSettings.leo & myLeoSettings.leo
    public globalBindingsDict!: g.SettingsDict;

    public files: string[]; // List of files to be loaded.
    public options: { [key: string]: any }; // Dictionary of user options. Keys are option names.
    public old_argv: string[]; // A copy of sys.argv for debugging.
    public more_cmdline_files: boolean; // True when more files remain on the command line to be loaded.

    // Themes.
    public leo_settings_c: Commands | undefined;
    public leo_settings_path: string | undefined;
    public my_settings_c: Commands | undefined;
    public my_settings_path: string | undefined;
    public theme_c: Commands | undefined;
    // #1374.
    public theme_path: string | undefined;

    private _context: vscode.ExtensionContext | undefined;

    //@+others
    //@+node:ekr.20230917150336.52: *5*  LM.ctor
    constructor(p_context?: vscode.ExtensionContext) {
        if (p_context) {
            this._context = p_context;
        }
        // this.globalSettingsDict = undefined;
        // this.globalBindingsDict = undefined;
        this.files = [];
        this.options = {};
        this.old_argv = [];
        this.more_cmdline_files = false;
    }

    //@+node:ekr.20230917150336.53: *5* LM.Directory & file utils
    //@+node:ekr.20230917150336.57: *6* LM.computeStandardDirectories & helpers
    /**
     * Compute the locations of standard directories and
     * set the corresponding ivars.
     */
    public async computeStandardDirectories(): Promise<unknown> {
        const lm = this;
        const join = g.PYTHON_os_path_join;
        g.app.loadDir = lm.computeLoadDir(); // UNUSED The leo / core directory.
        g.app.globalConfigDir = lm.computeGlobalConfigDir(); // UNUSED leo / config directory
        g.app.homeDir = await lm.computeHomeDir(); // * The user's home directory.
        g.app.homeLeoDir = await lm.computeHomeLeoDir(); // * The user's home/.leo directory.
        // g.app.leoDir = lm.computeLeoDir(); // * not used in leojs
        // These use g.app.loadDir...
        g.app.extensionsDir = ''; // join(g.app.loadDir, '..', 'extensions'); // UNSUSED The leo / extensions directory
        // g.app.leoEditorDir = join(g.app.loadDir, '..', '..');
        g.app.testDir = join(g.app.loadDir, '..', 'test');

        return;
    }

    //@+node:ekr.20230917150336.70: *5* LM.Settings
    //@+node:ekr.20230917150336.71: *6* LM.computeBindingLetter
    public computeBindingLetter(c: Commands, p_path: string): string {
        const lm = this;
        if (!p_path) {
            return 'D';
        }
        p_path = p_path.toLowerCase();
        const table = [
            ['M', 'myLeoSettings.leo'],
            [' ', 'leoSettings.leo'],
            ['F', c.shortFileName()],
        ];
        for (let p_entry of table) {
            let letter;
            let path2;
            [letter, path2] = p_entry;
            if (path2 && p_path.endsWith(path2.toLowerCase())) {
                return letter;
            }
        }
        if (lm.theme_path && p_path.endsWith(lm.theme_path.toLowerCase())) {
            return 'T';
        }
        if (p_path === 'register-command' || p_path.indexOf('mode') > -1) {
            return '@';
        }
        return 'D';
    }
    //@+node:ekr.20230917150336.73: *6* LM.createDefaultSettingsDicts
    /**
     * Create lm.globalSettingsDict & lm.globalBindingsDict.
     */
    public createDefaultSettingsDicts(): [g.SettingsDict, g.SettingsDict] {
        const settings_d = new g.SettingsDict('lm.globalSettingsDict');

        settings_d.setName('lm.globalSettingsDict');

        const bindings_d = new g.SettingsDict('lm.globalBindingsDict');

        return [settings_d, bindings_d];
    }

    //@+node:ekr.20230917150336.74: *6* LM.createSettingsDicts
    public createSettingsDicts(
        c: Commands,
        localFlag: boolean
    ): [g.SettingsDict | undefined, g.SettingsDict | undefined] {
        if (c) {
            // returns the *raw* shortcutsDict, not a *merged* shortcuts dict.
            const parser = new SettingsTreeParser(c, localFlag);
            let shortcutsDict;
            let settingsDict;
            [shortcutsDict, settingsDict] = parser.traverse();
            return [shortcutsDict, settingsDict];
        }
        return [undefined, undefined];
    }

    //@+node:ekr.20230917150336.103: *5* LM.revertCommander
    /**
     * Revert c to the previously saved contents.
     */
    public async revertCommander(c: Commands): Promise<void> {
        const lm: LoadManager = this;
        const fn: string = c.mFileName;
        // Re-read the file.
        // const theFile = lm.openAnyLeoFile(fn);

        const w_uri = g.makeVscodeUri(fn);

        try {
            await vscode.workspace.fs.stat(w_uri);
            // OK exists
            c.fileCommands.initIvars();
            await c.fileCommands.getLeoFile(undefined, fn, undefined, undefined, false);
        } catch {
            // Does not exist !
        }
    }
    //@-others
}
//@+node:ekr.20230917150336.104: *4* class PreviousSettings
/**
 * A class holding the settings and shortcuts dictionaries
 * that are computed in the first pass when loading local
 * files and passed to the second pass.
 */
export class PreviousSettings {
    public settingsDict: g.SettingsDict | undefined;
    public shortcutsDict: g.SettingsDict | undefined;

    constructor(
        settingsDict: g.SettingsDict | undefined,
        shortcutsDict: g.SettingsDict | undefined
    ) {
        if (!shortcutsDict || !settingsDict) {
            // #1766: unit tests.
            const lm = g.app.loadManager!;
            [settingsDict, shortcutsDict] = lm.createDefaultSettingsDicts();
        }
        this.settingsDict = settingsDict;
        this.shortcutsDict = shortcutsDict;
    }

    // = () : trick for toString as per https://stackoverflow.com/a/35361695/920301
    public toString = (): string => {
        return (
            `<PreviousSettings\n` +
            `${this.settingsDict}\n` +
            `${this.shortcutsDict}\n>`
        );
    };
}
//@+node:ekr.20230917151133.1: *3* From leoBody.ts (condensed)
//@+node:ekr.20230917151133.2: *4* class LeoBodyProvider
/**
 * * Body panes implementation as a file system using "leojs" as a scheme identifier
 */
export class LeoBodyProvider implements vscode.FileSystemProvider {

    // * Flag normally false
    public preventSaveToLeo: boolean = false;
    private _errorRefreshFlag: boolean = false;

    constructor(private _leoUi: LeoUI) { }

    //@+others
    //@+node:ekr.20230917151133.3: *5* setNewBodyUriTime
    /**
     * * Sets selected node body's modified time for this gnx virtual file
     * @param p_uri URI of file for which to set made-up modified time
     */
    public setNewBodyUriTime(p_uri: vscode.Uri): void {
        const w_gnx = utils.leoUriToStr(p_uri);
        this._lastBodyTimeGnx = w_gnx;
        this._setOpenedBodyTime(w_gnx);
    }

    //@+node:ekr.20230917151133.4: *5* _setOpenedBodyTime
    /**
     * * Adds entries in _openedBodiesGnx and _openedBodiesInfo if needed
     * * and sets the modified time of an opened body.
     */
    private _setOpenedBodyTime(p_gnx: string): void {
        const w_now = new Date().getTime();
        let w_created = w_now;
        if (!this._openedBodiesGnx.includes(p_gnx)) {
            this._openedBodiesGnx.push(p_gnx);
        } else {
            w_created = this._openedBodiesInfo[p_gnx].ctime; // Already created?
        }
        this._openedBodiesInfo[p_gnx] = {
            ctime: w_created, // w_now, // maybe kept.
            mtime: w_now // new 'modified' time for sure.
        };
    }

    //@+node:ekr.20230917151133.5: *5* fireRefreshFile
    /**
     * * Refresh the body pane for a particular gnx by telling vscode that the file from the Leo file provider has changed
     * @param p_gnx Gnx of body associated with this virtual file, mostly Leo's selected node
     */
    public fireRefreshFile(p_gnx: string): void {

        if (!this._openedBodiesGnx.includes(p_gnx)) {
            console.error("ASKED TO REFRESH NOT EVEN IN SELECTED BODY: ", p_gnx);
        }

        this._setOpenedBodyTime(p_gnx);

        this._onDidChangeFileEmitter.fire([{
            type: vscode.FileChangeType.Changed,
            uri: utils.strToLeoUri(p_gnx)
        }]);
    }

    //@+node:ekr.20230917151133.6: *5* refreshPossibleGnxList
    /**
     * ? Maybe deprecated 
     * * Refreshes the '_possibleGnxList' list of all unique gnx from Leo
     * @returns a 'fresh' gnx string array
     */
    public refreshPossibleGnxList(): string[] {
        // * Get updated list of possible gnx

        // all_gnx = [p.v.gnx for p in c.all_unique_positions(copy=False)]
        const c = g.app.windowList[this._leoUi.frameIndex].c;
        return [...c.all_unique_positions(false)].map(p => p.v.gnx);
    }

    //@+node:ekr.20230917151133.7: *5* watch
    public watch(p_resource: vscode.Uri, p_options: { readonly recursive: boolean; readonly excludes: readonly string[] }): vscode.Disposable {
        const w_gnx = utils.leoUriToStr(p_resource);
        if (!this._watchedBodiesGnx.includes(w_gnx)) {
            this._watchedBodiesGnx.push(w_gnx); // add gnx
        }
        // else already in list
        return new vscode.Disposable(() => {
            const w_position = this._watchedBodiesGnx.indexOf(w_gnx); // find and remove it
            if (w_position > -1) {
                this._watchedBodiesGnx.splice(w_position, 1);
            }
        });
    }

    //@+node:ekr.20230917151133.8: *5* stat
    public stat(p_uri: vscode.Uri): vscode.FileStat {
        if (this._leoUi.leoStates.fileOpenedReady) {
            const w_gnx = utils.leoUriToStr(p_uri);
            if (p_uri.fsPath.length === 1) {
                return { type: vscode.FileType.Directory, ctime: 0, mtime: 0, size: 0 };
            } else if (false && w_gnx === this._lastGnx && this._openedBodiesGnx.includes(this._lastGnx)) {
                // ! Always return current size: w_v.b.length ! Not this._lastBodyLength !
                console.log('had stats: modified: ', this._openedBodiesInfo[this._lastGnx].mtime);
                return {
                    type: vscode.FileType.File,
                    ctime: this._openedBodiesInfo[this._lastGnx].ctime,
                    mtime: this._openedBodiesInfo[this._lastGnx].mtime,
                    size: this._lastBodyLength
                };
            } else if (this._openedBodiesGnx.includes(w_gnx)) {
                const c = g.app.windowList[this._leoUi.frameIndex].c;
                const w_v = c.fileCommands.gnxDict[w_gnx];
                return {
                    type: vscode.FileType.File,
                    ctime: this._openedBodiesInfo[w_gnx].ctime,
                    mtime: this._openedBodiesInfo[w_gnx].mtime,
                    size: w_v.b.length
                };
            }
        }
        // throw vscode.FileSystemError.FileNotFound();
        // (Instead of FileNotFound) should be caught by _onActiveEditorChanged or _changedVisibleTextEditors
        return { type: vscode.FileType.File, ctime: 0, mtime: 0, size: 0 };
    }

    //@+node:ekr.20230917151133.9: *5* readFile
    public readFile(p_uri: vscode.Uri): Uint8Array {
        if (this._leoUi.leoStates.fileOpenedReady) {
            if (p_uri.fsPath.length === 1) { // p_uri.fsPath === '/' || p_uri.fsPath === '\\'
                throw vscode.FileSystemError.FileIsADirectory();
            } else {
                const w_gnx = utils.leoUriToStr(p_uri);

                if (!this._openedBodiesGnx.includes(w_gnx)) {
                    console.log(
                        " _openedBodiesGnx length: ", this._openedBodiesGnx.length,
                        '\n *** readFile: ERROR File not in _openedBodiesGnx! readFile missing refreshes? gnx: ', w_gnx
                    );
                }

                const c = g.app.windowList[this._leoUi.frameIndex].c;
                const w_v = c.fileCommands.gnxDict[w_gnx];
                if (w_v) {
                    this._errorRefreshFlag = false; // got body so reset possible flag!
                    this._lastGnx = w_gnx;
                    this._lastBodyData = w_v.b;
                    const w_buffer: Uint8Array = Buffer.from(this._lastBodyData);
                    this._lastBodyLength = w_buffer.byteLength;
                    return w_buffer;
                } else {
                    if (!this._errorRefreshFlag) {
                        this._leoUi.fullRefresh();
                    }
                    if (this._lastGnx === w_gnx) {
                        // was last gnx of closed file about to be switched to new document selected
                        console.log('Passed in not found: ' + w_gnx);
                        return Buffer.from(this._lastBodyData);
                    }
                    console.error("ERROR => readFile of unknown GNX"); // is possibleGnxList updated correctly?
                    return Buffer.from("");
                }
            }
        } else {
            throw vscode.FileSystemError.FileNotFound();
        }
    }

    //@+node:ekr.20230917151133.10: *5* readDirectory
    public readDirectory(p_uri: vscode.Uri): [string, vscode.FileType][] {
        if (p_uri.fsPath.length === 1) { // p_uri.fsPath === '/' || p_uri.fsPath === '\\'
            const w_directory: [string, vscode.FileType][] = [];
            w_directory.push([this._lastBodyTimeGnx, vscode.FileType.File]);
            return w_directory;
        } else {
            throw vscode.FileSystemError.FileNotFound(p_uri);
        }
    }

    //@+node:ekr.20230917151133.11: *5* createDirectory
    public createDirectory(p_uri: vscode.Uri): void {
        console.warn('Called createDirectory with ', p_uri.fsPath); // should not happen
        throw vscode.FileSystemError.NoPermissions();
    }

    //@+node:ekr.20230917151133.12: *5* writeFile
    public writeFile(p_uri: vscode.Uri, p_content: Uint8Array, p_options: { create: boolean, overwrite: boolean }): void {
        if (!this.preventSaveToLeo) {
            void this._leoUi.triggerBodySave(true); // Might have been a vscode 'save' via the menu
        } else {
            this.preventSaveToLeo = false;
        }
        const w_gnx = utils.leoUriToStr(p_uri);
        if (!this._openedBodiesGnx.includes(w_gnx)) {
            console.error("LeoJS: Tried to save body other than selected node's body", w_gnx);
        }
        this._setOpenedBodyTime(w_gnx);
        this._fireSoon({ type: vscode.FileChangeType.Changed, uri: p_uri });
    }

    //@+node:ekr.20230917151133.13: *5* rename
    public rename(p_oldUri: vscode.Uri, p_newUri: vscode.Uri, p_options: { overwrite: boolean }): void {
        console.warn('Called rename on ', p_oldUri.fsPath, p_newUri.fsPath); // should not happen
        this._fireSoon(
            { type: vscode.FileChangeType.Deleted, uri: p_oldUri },
            { type: vscode.FileChangeType.Created, uri: p_newUri }
        );
    }

    //@+node:ekr.20230917151133.14: *5* delete
    public delete(p_uri: vscode.Uri): void {
        const w_gnx = utils.leoUriToStr(p_uri);
        if (this._openedBodiesGnx.includes(w_gnx)) {
            this._openedBodiesGnx.splice(this._openedBodiesGnx.indexOf(w_gnx), 1);
            delete this._openedBodiesInfo[w_gnx];
        } else {
            // console.log("not deleted");
        }

        // dirname is just a slash "/"
        let w_dirname = p_uri.with({ path: path.posix.dirname(p_uri.path) });

        this._fireSoon(
            { type: vscode.FileChangeType.Changed, uri: w_dirname },
            { uri: p_uri, type: vscode.FileChangeType.Deleted }
        );
    }

    //@+node:ekr.20230917151133.15: *5* copy
    public copy(p_uri: vscode.Uri): void {
        console.warn('Called copy on ', p_uri.fsPath); // should not happen
        throw vscode.FileSystemError.NoPermissions();
    }

    //@+node:ekr.20230917151133.16: *5* _fireSoon
    private _fireSoon(...p_events: vscode.FileChangeEvent[]): void {
        this._bufferedEvents.push(...p_events);
        if (this._fireSoonHandle) {
            clearTimeout(this._fireSoonHandle);
        }
        this._fireSoonHandle = setTimeout(() => {
            this._onDidChangeFileEmitter.fire(this._bufferedEvents);
            this._bufferedEvents.length = 0; // clearing events array
        }, 5);
    }

    //@-others
}
//@-others

//@@language typescript
//@@tabwidth -4
//@@pagewidth 70
//@-leo
