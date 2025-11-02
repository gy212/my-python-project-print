const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow;
let backendProcess;

// Disable GPU to reduce white-screen issues on some devices.
app.disableHardwareAcceleration();

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    backgroundColor: '#1F2937',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    frame: false,
    titleBarStyle: 'hidden',
    icon: path.join(__dirname, 'icon.ico')
  });

  // 修复UI文件路径
  const uiPath = path.join(__dirname, '..', 'frontend', 'ui.html');
  mainWindow.loadFile(uiPath);
  mainWindow.setHasShadow(true);

  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function getBackendLaunchConfig() {
  if (app.isPackaged) {
    const packagedBackend = path.join(process.resourcesPath, 'backend', 'backend-service.exe');
    if (!fs.existsSync(packagedBackend)) {
      console.error('[Backend] Packaged executable not found:', packagedBackend);
      return null;
    }
    return {
      command: packagedBackend,
      args: [],
      options: {
        cwd: path.dirname(packagedBackend)
      }
    };
  }

  const backendScript = path.join(__dirname, 'backend.py');
  if (!fs.existsSync(backendScript)) {
    console.error('[Backend] backend.py not found at', backendScript);
    return null;
  }

  let pythonCmd = 'python';
  if (process.platform === 'win32') {
    // 修复虚拟环境路径 - 从项目根目录查找
    const projectRoot = path.join(__dirname, '..', '..');
    const venvPython = path.join(projectRoot, '.venv', 'Scripts', 'python.exe');
    if (fs.existsSync(venvPython)) {
      pythonCmd = venvPython;
    }
  }

  return {
    command: pythonCmd,
    args: [backendScript],
    options: {
      cwd: __dirname
    }
  };
}

function startBackend() {
  const config = getBackendLaunchConfig();
  if (!config) {
    return;
  }

  backendProcess = spawn(config.command, config.args, {
    cwd: config.options.cwd,
    env: process.env,
    windowsHide: false
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  backendProcess.on('close', (code) => {
    console.log(`Backend exited with code ${code}`);
  });
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
}

app.on('ready', () => {
  startBackend();
  setTimeout(createWindow, 1500);
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});

ipcMain.on('window-close', () => {
  if (mainWindow) {
    mainWindow.close();
  }
});

ipcMain.on('window-minimize', () => {
  if (mainWindow) {
    mainWindow.minimize();
  }
});

ipcMain.on('window-maximize', () => {
  if (!mainWindow) {
    return;
  }
  if (mainWindow.isMaximized()) {
    mainWindow.unmaximize();
  } else {
    mainWindow.maximize();
  }
});

ipcMain.on('window-always-on-top', (_event, flag) => {
  if (mainWindow) {
    mainWindow.setAlwaysOnTop(!!flag);
  }
});
