<?php
// config.php - Configuration and utility functions

class MinecraftServerManager {
    private const PISTON_META_MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json";
    private static $serverProcess = null;
    private static $logFile = null;
    
    public static function fetchJson($url) {
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'header' => 'User-Agent: Mozilla/5.0 (MCserverPy-PHP Setup)',
                'timeout' => 60
            ]
        ]);
        
        $data = file_get_contents($url, false, $context);
        if ($data === false) {
            throw new Exception("Failed to fetch data from $url");
        }
        
        return json_decode($data, true);
    }
    
    public static function getAvailableVersions() {
        try {
            $manifest = self::fetchJson(self::PISTON_META_MANIFEST);
            $versions = $manifest['versions'] ?? [];
            $latestRelease = $manifest['latest']['release'] ?? '';
            $latestSnapshot = $manifest['latest']['snapshot'] ?? '';
            
            // Filter to releases and recent snapshots
            $releases = array_slice(array_filter($versions, fn($v) => $v['type'] === 'release'), 0, 20);
            $snapshots = array_slice(array_filter($versions, fn($v) => $v['type'] === 'snapshot'), 0, 10);
            
            return [
                'latest_release' => $latestRelease,
                'latest_snapshot' => $latestSnapshot,
                'releases' => $releases,
                'snapshots' => $snapshots
            ];
        } catch (Exception $e) {
            return ['error' => $e->getMessage()];
        }
    }
    
    public static function getVersionInfo($version = 'latest') {
        $manifest = self::fetchJson(self::PISTON_META_MANIFEST);
        
        if (!$version || $version === 'latest') {
            $versionId = $manifest['latest']['release'] ?? null;
            if (!$versionId) {
                throw new Exception("Could not determine latest release");
            }
        } else {
            $versionId = $version;
        }
        
        $versions = $manifest['versions'] ?? [];
        $selected = null;
        
        foreach ($versions as $v) {
            if ($v['id'] === $versionId) {
                $selected = $v;
                break;
            }
        }
        
        if (!$selected) {
            if (in_array($version, ['latest-snapshot', 'snapshot'])) {
                $snapId = $manifest['latest']['snapshot'] ?? null;
                if (!$snapId) {
                    throw new Exception("Could not determine latest snapshot");
                }
                foreach ($versions as $v) {
                    if ($v['id'] === $snapId) {
                        $selected = $v;
                        $versionId = $snapId;
                        break;
                    }
                }
            }
            if (!$selected) {
                throw new Exception("Version '$versionId' not found");
            }
        }
        
        $versionMeta = self::fetchJson($selected['url']);
        $serverDownload = $versionMeta['downloads']['server'] ?? null;
        
        if (!$serverDownload) {
            throw new Exception("No server download found for version $versionId");
        }
        
        return [$versionId, $serverDownload];
    }
    
    public static function checkJavaVersion() {
        $output = shell_exec('java -version 2>&1');
        if (!$output) {
            return [false, 'java not found in PATH'];
        }
        
        // Extract version number
        preg_match('/version "([^"]+)"/', $output, $matches);
        $versionStr = $matches[1] ?? '';
        
        $isOk = false;
        if ($versionStr) {
            $major = (int)explode('.', $versionStr)[0];
            $isOk = $major >= 17;
        } else {
            // Fallback check
            $isOk = strpos($output, '17') !== false || 
                   strpos($output, '18') !== false || 
                   strpos($output, '19') !== false || 
                   strpos($output, '20') !== false || 
                   strpos($output, '21') !== false;
        }
        
        return [$isOk, $output];
    }
    
    public static function ensureDir($path) {
        if (!is_dir($path)) {
            mkdir($path, 0755, true);
        }
    }
    
    public static function downloadFile($url, $destPath, $progressCallback = null) {
        $tmpPath = $destPath . '.part';
        
        $context = stream_context_create([
            'http' => [
                'method' => 'GET',
                'header' => 'User-Agent: Mozilla/5.0 (MCserverPy-PHP Setup)',
                'timeout' => 300
            ]
        ]);
        
        $source = fopen($url, 'rb', false, $context);
        $dest = fopen($tmpPath, 'wb');
        
        if (!$source || !$dest) {
            throw new Exception("Failed to open streams for download");
        }
        
        $downloaded = 0;
        while (!feof($source)) {
            $chunk = fread($source, 64 * 1024);
            if ($chunk === false) break;
            
            fwrite($dest, $chunk);
            $downloaded += strlen($chunk);
            
            if ($progressCallback) {
                $progressCallback($downloaded);
            }
        }
        
        fclose($source);
        fclose($dest);
        
        // Move to final location
        if (file_exists($destPath)) {
            unlink($destPath);
        }
        rename($tmpPath, $destPath);
    }
    
    public static function sha1File($path) {
        return sha1_file($path);
    }
    
    public static function writeEula($serverDir, $acceptEula) {
        $eulaPath = $serverDir . DIRECTORY_SEPARATOR . 'eula.txt';
        $content = "# By changing the setting below to TRUE you are indicating your agreement to the EULA\n";
        $content .= "# https://aka.ms/MinecraftEULA\n";
        $content .= "eula=" . ($acceptEula ? 'true' : 'false') . "\n";
        
        file_put_contents($eulaPath, $content);
        return $eulaPath;
    }
    
    public static function writeStartScripts($serverDir, $minMem, $maxMem, $nogui = true, $jvmFlags = '') {
        $jvmFlagsStr = $jvmFlags ? ' ' . $jvmFlags : '';
        $cmd = "java -Xms{$minMem} -Xmx{$maxMem}{$jvmFlagsStr} -jar server.jar" . ($nogui ? ' nogui' : '');
        
        // Windows batch file
        $batPath = $serverDir . DIRECTORY_SEPARATOR . 'start.bat';
        $batContent = "@echo off\n";
        $batContent .= "REM Generated by MCserverPy-PHP setup script\n";
        $batContent .= "$cmd\n";
        $batContent .= "pause\n";
        file_put_contents($batPath, $batContent);
        
        // Unix shell script
        $shPath = $serverDir . DIRECTORY_SEPARATOR . 'start.sh';
        $shContent = "#!/usr/bin/env bash\n";
        $shContent .= "# Generated by MCserverPy-PHP setup script\n";
        $shContent .= "$cmd\n";
        file_put_contents($shPath, $shContent);
        chmod($shPath, 0755);
        
        return [$batPath, $shPath];
    }
    
    public static function startServer($serverDir, $minMem, $maxMem, $nogui = true, $jvmFlags = '', $foreground = false) {
        $jarPath = $serverDir . DIRECTORY_SEPARATOR . 'server.jar';
        if (!file_exists($jarPath)) {
            throw new Exception('server.jar not found. Run setup first.');
        }
        
        $pidFile = $serverDir . DIRECTORY_SEPARATOR . 'server.pid';
        $logFile = $serverDir . DIRECTORY_SEPARATOR . 'server_php.log';
        
        // Check if already running
        if (file_exists($pidFile)) {
            $pid = (int)file_get_contents($pidFile);
            if (self::isProcessRunning($pid)) {
                throw new Exception('Server is already running (PID: ' . $pid . ')');
            }
        }
        
        $jvmFlagsStr = $jvmFlags ? ' ' . $jvmFlags : '';
        $noguiStr = $nogui ? ' nogui' : '';
        
        // For Windows, handle foreground mode differently
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            if ($foreground) {
                // Start in foreground with visible console window
                $cmd = sprintf('start "Minecraft Server" cmd /k "cd /d %s && java -Xms%s -Xmx%s%s -jar server.jar%s"',
                    escapeshellarg($serverDir),
                    escapeshellarg($minMem),
                    escapeshellarg($maxMem),
                    $jvmFlagsStr,
                    $noguiStr
                );
                shell_exec($cmd);
                // For foreground mode, we can't easily track PID, so just mark as running
                file_put_contents($pidFile, 'foreground');
                return ['status' => 'started', 'pid' => 'foreground', 'mode' => 'foreground'];
            } else {
                // Background mode - use PowerShell for better process control
                $cmd = sprintf('powershell -Command "Start-Process -FilePath java -ArgumentList \'-Xms%s\', \'-Xmx%s\'%s, \'-jar\', \'server.jar\'%s -WindowStyle Hidden -PassThru | ForEach-Object { $_.Id } | Out-File -FilePath \'%s\' -Encoding ascii"',
                    $minMem,
                    $maxMem,
                    $jvmFlagsStr ? ', \'' . str_replace('\'', '\'\'', $jvmFlagsStr) . '\'' : '',
                    $noguiStr ? ', \'nogui\'' : '',
                    str_replace('\\', '\\\\', $pidFile)
                );
            }
        } else {
            // Unix systems
            if ($foreground) {
                // Start in foreground (blocking)
                $cmd = sprintf('java -Xms%s -Xmx%s%s -jar server.jar%s',
                    escapeshellarg($minMem),
                    escapeshellarg($maxMem),
                    $jvmFlagsStr,
                    $noguiStr
                );
                // Note: This will block the PHP process
                chdir($serverDir);
                passthru($cmd);
                return ['status' => 'started', 'pid' => 'foreground', 'mode' => 'foreground'];
            } else {
                // Background mode
                $cmd = sprintf('java -Xms%s -Xmx%s%s -jar server.jar%s > %s 2>&1 & echo $! > %s',
                    escapeshellarg($minMem),
                    escapeshellarg($maxMem),
                    $jvmFlagsStr,
                    $noguiStr,
                    escapeshellarg($logFile),
                    escapeshellarg($pidFile)
                );
            }
        }
        
        chdir($serverDir);
        $output = shell_exec($cmd);
        
        // Give it a moment to start
        sleep(1);
        
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            // On Windows, check if we successfully got a PID
            sleep(2); // Give PowerShell time to write PID
            if (file_exists($pidFile)) {
                $pidContent = trim(file_get_contents($pidFile));
                if ($pidContent && $pidContent !== 'foreground') {
                    $pid = (int)$pidContent;
                    if (self::isProcessRunning($pid)) {
                        return ['status' => 'started', 'pid' => $pid, 'mode' => 'background'];
                    }
                }
            }
            // Fallback: check by process name
            $processes = shell_exec('tasklist /FI "IMAGENAME eq java.exe" /FO CSV');
            if (strpos($processes, 'java.exe') !== false) {
                file_put_contents($pidFile, 'running'); // Just a marker
                return ['status' => 'started', 'pid' => 'unknown', 'mode' => 'background'];
            } else {
                throw new Exception('Failed to start server');
            }
        } else {
            if (file_exists($pidFile)) {
                $pid = (int)file_get_contents($pidFile);
                return ['status' => 'started', 'pid' => $pid, 'mode' => 'background'];
            } else {
                throw new Exception('Failed to start server');
            }
        }
    }
    
    public static function stopServer($serverDir) {
        $pidFile = $serverDir . DIRECTORY_SEPARATOR . 'server.pid';
        
        if (!file_exists($pidFile)) {
            throw new Exception('Server is not running');
        }
        
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            // On Windows, kill all java processes (crude but works for demo)
            shell_exec('taskkill /F /IM java.exe');
        } else {
            $pid = (int)file_get_contents($pidFile);
            if (!self::isProcessRunning($pid)) {
                unlink($pidFile);
                throw new Exception('Server is not running');
            }
            shell_exec("kill $pid");
        }
        
        unlink($pidFile);
        return ['status' => 'stopped'];
    }
    
    public static function getServerStatus($serverDir) {
        $pidFile = $serverDir . DIRECTORY_SEPARATOR . 'server.pid';
        
        if (!file_exists($pidFile)) {
            return ['status' => 'not_started'];
        }
        
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            $processes = shell_exec('tasklist /FI "IMAGENAME eq java.exe" /FO CSV');
            if (strpos($processes, 'java.exe') !== false) {
                return ['status' => 'running', 'pid' => 'unknown'];
            } else {
                unlink($pidFile);
                return ['status' => 'stopped'];
            }
        } else {
            $pid = (int)file_get_contents($pidFile);
            if (self::isProcessRunning($pid)) {
                return ['status' => 'running', 'pid' => $pid];
            } else {
                unlink($pidFile);
                return ['status' => 'stopped'];
            }
        }
    }
    
    public static function getServerLogs($serverDir, $lines = 50, $source = 'auto') {
        $latestLog = $serverDir . DIRECTORY_SEPARATOR . 'logs' . DIRECTORY_SEPARATOR . 'latest.log';
        $phpLog = $serverDir . DIRECTORY_SEPARATOR . 'server_php.log';

        // Decide candidates based on requested source
        $candidates = [];
        switch (strtolower($source)) {
            case 'latest':
                $candidates = [$latestLog];
                break;
            case 'php':
                $candidates = [$phpLog];
                break;
            case 'auto':
            default:
                $candidates = [$latestLog, $phpLog];
                break;
        }

        $logFile = null;
        foreach ($candidates as $cand) {
            if (file_exists($cand)) { $logFile = $cand; break; }
        }

        if (!$logFile || !file_exists($logFile)) {
            return ['logs' => []];
        }

        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            // Windows - use PowerShell to get last N lines (escape single quotes)
            $escaped = str_replace("'", "''", $logFile);
            $cmd = "powershell -Command \"Get-Content '$escaped' -Tail $lines\"";
        } else {
            // Unix - use tail
            $cmd = "tail -n $lines " . escapeshellarg($logFile);
        }

        $output = shell_exec($cmd);
        $logLines = $output ? explode("\n", trim($output)) : [];

        return ['logs' => $logLines, 'source' => (strpos($logFile, 'latest.log') !== false ? 'latest' : 'php')];
    }
    
    private static function isProcessRunning($pid) {
        if (strtoupper(substr(PHP_OS, 0, 3)) === 'WIN') {
            $output = shell_exec("tasklist /FI \"PID eq $pid\" /FO CSV");
            return strpos($output, (string)$pid) !== false;
        } else {
            $output = shell_exec("ps -p $pid");
            return strpos($output, (string)$pid) !== false;
        }
    }
}
?>