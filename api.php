<?php
require_once __DIR__ . '/config.php';

header('Content-Type: application/json');

$path = $_GET['action'] ?? '';

try {
    switch ($path) {
        case 'versions':
            echo json_encode(MinecraftServerManager::getAvailableVersions());
            break;
        case 'java':
            [$ok, $output] = MinecraftServerManager::checkJavaVersion();
            echo json_encode(['ok' => $ok, 'output' => $output]);
            break;
        case 'setup':
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $version = $input['version'] ?? 'latest';
            $serverDir = realpath('.') . DIRECTORY_SEPARATOR . ($input['serverDir'] ?? 'mc_server');
            $minMemory = $input['minMemory'] ?? '1G';
            $maxMemory = $input['maxMemory'] ?? '2G';
            $acceptEula = $input['acceptEula'] ?? false;
            $forceDownload = $input['forceDownload'] ?? false;
            $nogui = isset($input['nogui']) ? (bool)$input['nogui'] : true;
            $jvmFlags = trim($input['jvmFlags'] ?? '');

            MinecraftServerManager::ensureDir($serverDir);
            [$versionId, $serverDownload] = MinecraftServerManager::getVersionInfo($version);
            $url = $serverDownload['url'] ?? null;
            $expectedSha1 = $serverDownload['sha1'] ?? null;
            if (!$url) throw new Exception('Missing server download URL');

            $jarPath = $serverDir . DIRECTORY_SEPARATOR . 'server.jar';
            if (!file_exists($jarPath) || $forceDownload) {
                MinecraftServerManager::downloadFile($url, $jarPath);
            }

            if ($expectedSha1 && file_exists($jarPath)) {
                $actualSha1 = MinecraftServerManager::sha1File($jarPath);
                if (strtolower($actualSha1) !== strtolower($expectedSha1)) {
                    throw new Exception('SHA1 mismatch for server.jar');
                }
            }

            MinecraftServerManager::writeEula($serverDir, $acceptEula);
            MinecraftServerManager::writeStartScripts($serverDir, $minMemory, $maxMemory, $nogui, $jvmFlags);

            echo json_encode(['status' => 'ok', 'version' => $versionId, 'serverDir' => $serverDir]);
            break;
        case 'start':
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $serverDir = realpath('.') . DIRECTORY_SEPARATOR . ($input['serverDir'] ?? 'mc_server');
            $minMemory = $input['minMemory'] ?? '1G';
            $maxMemory = $input['maxMemory'] ?? '2G';
            $nogui = isset($input['nogui']) ? (bool)$input['nogui'] : true;
            $jvmFlags = trim($input['jvmFlags'] ?? '');
            $foreground = isset($input['foreground']) ? (bool)$input['foreground'] : false;
            $res = MinecraftServerManager::startServer($serverDir, $minMemory, $maxMemory, $nogui, $jvmFlags, $foreground);
            echo json_encode($res);
            break;
        case 'stop':
            $input = json_decode(file_get_contents('php://input'), true) ?? [];
            $serverDir = realpath('.') . DIRECTORY_SEPARATOR . ($input['serverDir'] ?? 'mc_server');
            $res = MinecraftServerManager::stopServer($serverDir);
            echo json_encode($res);
            break;
        case 'status':
            $serverDir = realpath('.') . DIRECTORY_SEPARATOR . ($_GET['serverDir'] ?? 'mc_server');
            $res = MinecraftServerManager::getServerStatus($serverDir);
            echo json_encode($res);
            break;
        case 'logs':
            $serverDir = realpath('.') . DIRECTORY_SEPARATOR . ($_GET['serverDir'] ?? 'mc_server');
            $lines = isset($_GET['lines']) ? max(10, (int)$_GET['lines']) : 100;
            $source = $_GET['source'] ?? 'auto'; // latest, php, auto
            $res = MinecraftServerManager::getServerLogs($serverDir, $lines, $source);
            echo json_encode($res);
            break;
        case 'properties':
            $serverDir = $_GET['serverDir'] ?? '';
            if (empty($serverDir)) {
                $input = json_decode(file_get_contents('php://input'), true) ?? [];
                $serverDir = $input['serverDir'] ?? '';
            }
            
            $serverDir = realpath('.') . DIRECTORY_SEPARATOR . $serverDir;
            $propertiesFile = $serverDir . DIRECTORY_SEPARATOR . 'server.properties';
            
            // Handle POST request to save properties
            if ($_SERVER['REQUEST_METHOD'] === 'POST') {
                $input = json_decode(file_get_contents('php://input'), true) ?? [];
                $properties = $input['properties'] ?? [];
                
                if (!is_dir($serverDir)) {
                    throw new Exception('Server directory does not exist');
                }
                
                // Read existing properties or create default
                $existingProps = [];
                if (file_exists($propertiesFile)) {
                    $lines = file($propertiesFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
                    foreach ($lines as $line) {
                        if (strpos($line, '#') === 0) continue; // Skip comments
                        $parts = explode('=', $line, 2);
                        if (count($parts) === 2) {
                            $existingProps[trim($parts[0])] = trim($parts[1]);
                        }
                    }
                }
                
                // Merge with new properties
                $mergedProps = array_merge($existingProps, $properties);
                
                // Write properties file
                $content = "#Minecraft server properties\n#" . date('D M d H:i:s T Y') . "\n";
                foreach ($mergedProps as $key => $value) {
                    $content .= "$key=$value\n";
                }
                
                file_put_contents($propertiesFile, $content);
                echo json_encode(['status' => 'ok', 'message' => 'Properties saved']);
            } 
            // Handle GET request to retrieve properties
            else {
                if (!file_exists($propertiesFile)) {
                    echo json_encode(['status' => 'error', 'message' => 'Properties file not found']);
                    break;
                }
                
                $properties = [];
                $lines = file($propertiesFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
                foreach ($lines as $line) {
                    if (strpos($line, '#') === 0) continue; // Skip comments
                    $parts = explode('=', $line, 2);
                    if (count($parts) === 2) {
                        $properties[trim($parts[0])] = trim($parts[1]);
                    }
                }
                
                echo json_encode(['status' => 'ok', 'properties' => $properties]);
            }
            break;
        default:
            http_response_code(404);
            echo json_encode(['error' => 'Unknown action']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}