import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart'; // Handles operating system directory picking
import 'api_service.dart';
import 'b2_downloader.dart';

void main() {
  runApp(const DataSyncApp());
}

class DataSyncApp extends StatelessWidget {
  const DataSyncApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DataSync',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.deepPurple,
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0F0F15),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<dynamic> pendingFiles = [];
  String status = "Idle";
  bool isLoading = false;

  // Tracks user's custom download destination path
  String? customSyncFolder;

  Future<void> checkPending() async {
    setState(() {
      status = "Checking sync relay...";
      isLoading = true;
    });

    try {
      final results = await ApiService.pollPending();
      setState(() {
        pendingFiles = results;
        status = results.isEmpty ? "All synced up" : "Found ${results.length} pending file(s)";
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        status = "Connection failed";
        isLoading = false;
      });
    }
  }

  // Opens OS native directory browser selector
  Future<void> pickCustomFolder() async {
    String? selectedDirectory = await FilePicker.platform.getDirectoryPath();

    if (selectedDirectory != null) {
      setState(() {
        customSyncFolder = selectedDirectory;
      });
    }
  }

  IconData _getFileIcon(String filename) {
    final ext = filename.split('.').last.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].contains(ext)) return Icons.image_rounded;
    if (['mp4', 'mkv', 'mov', 'avi'].contains(ext)) return Icons.video_file_rounded;
    if (['mp3', 'wav', 'flac', 'm4a'].contains(ext)) return Icons.audiotrack_rounded;
    if (['pdf', 'doc', 'docx', 'txt'].contains(ext)) return Icons.description_rounded;
    if (['zip', 'rar', 'tar', 'gz'].contains(ext)) return Icons.folder_zip_rounded;
    return Icons.insert_drive_file_rounded;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: theme.colorScheme.primaryContainer.withOpacity(0.5),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.sync_rounded, color: theme.colorScheme.primary),
            ),
            const SizedBox(width: 12),
            const Text(
              'DataSync',
              style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 0.5),
            ),
          ],
        ),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 16.0),
            child: Chip(
              avatar: const Icon(Icons.phone_android_rounded, size: 14),
              label: Text(myDeviceId, style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600)),
              backgroundColor: theme.colorScheme.surfaceContainerHigh,
              side: BorderSide.none,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            ),
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status Panel Card
            Card(
              elevation: 0,
              color: theme.colorScheme.surfaceContainerLow,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(24),
                side: BorderSide(color: theme.colorScheme.outlineVariant.withOpacity(0.3)),
              ),
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'RELAY SERVICE STATUS',
                            style: theme.textTheme.labelSmall?.copyWith(
                              color: theme.colorScheme.onSurfaceVariant.withOpacity(0.7),
                              letterSpacing: 1.2,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            status,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: isLoading ? theme.colorScheme.primary : theme.colorScheme.onSurface,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    isLoading
                    ? const SizedBox(
                      width: 28,
                      height: 28,
                      child: CircularProgressIndicator(strokeWidth: 3),
                    )
                    : FilledButton.icon(
                      onPressed: checkPending,
                      icon: const Icon(Icons.refresh_rounded, size: 18),
                      label: const Text('Fetch'),
                      style: FilledButton.styleFrom(
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Custom Storage Directory Config Card
            Card(
              elevation: 0,
              color: theme.colorScheme.surfaceContainerLow.withOpacity(0.6),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
                side: BorderSide(color: theme.colorScheme.outlineVariant.withOpacity(0.15)),
              ),
              child: ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                leading: Icon(
                  Icons.folder_open_rounded,
                  color: customSyncFolder != null ? Colors.amber[400] : theme.colorScheme.onSurfaceVariant,
                ),
                title: Text(
                  customSyncFolder != null ? 'Custom Sync Folder' : 'Default Target Folder',
                  style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
                ),
                subtitle: Text(
                  customSyncFolder ?? 'App Documents Directory',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant.withOpacity(0.6),
                    overflow: TextOverflow.ellipsis,
                  ),
                  maxLines: 1,
                ),
                trailing: IconButton.filledTonal(
                  icon: Icon(customSyncFolder != null ? Icons.edit_calendar_rounded : Icons.add_circle_outline_rounded, size: 18),
                  onPressed: pickCustomFolder,
                ),
              ),
            ),
            const SizedBox(height: 24),

            // Section Label
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Incoming Files',
                  style: theme.textTheme.titleSmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.5,
                  ),
                ),
                if (pendingFiles.isNotEmpty)
                  Text(
                    '${pendingFiles.length} items available',
                    style: theme.textTheme.bodySmall?.copyWith(color: theme.colorScheme.primary),
                  ),
              ],
            ),
            const SizedBox(height: 12),

            // Transferred Files Container
            Expanded(
              child: pendingFiles.isEmpty
              ? Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: theme.colorScheme.surfaceContainerLow,
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        Icons.auto_awesome_motion_rounded,
                        size: 44,
                        color: theme.colorScheme.onSurfaceVariant.withOpacity(0.3),
                      ),
                    ),
                    const SizedBox(height: 20),
                    Text(
                      'Your queue is clear',
                      style: theme.textTheme.titleMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant.withOpacity(0.8),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'New cross-device items will arrive here.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant.withOpacity(0.5),
                      ),
                    ),
                  ],
                ),
              )
              : ListView.separated(
                itemCount: pendingFiles.length,
                separatorBuilder: (context, index) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final file = pendingFiles[index];
                  return Card(
                    margin: EdgeInsets.zero,
                    elevation: 0,
                    color: theme.colorScheme.surfaceContainerHigh,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: ListTile(
                      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                      leading: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.primary.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(
                          _getFileIcon(file['filename']),
                          color: theme.colorScheme.primary,
                        ),
                      ),
                      title: Text(
                        file['filename'],
                        style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 4.0),
                        child: Text(
                          'ID: ${file['file_key']}',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.onSurfaceVariant.withOpacity(0.6),
                            fontFamily: 'monospace',
                            fontSize: 11,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      trailing: IconButton.filledTonal(
                        icon: const Icon(Icons.download_rounded, size: 20),
                        onPressed: () async {
                          final downloader = B2Downloader();
                          // Passed customSyncFolder here!
                          await downloader.downloadFile(
                            fileKey: file['file_key'],
                            filename: file['filename'],
                            customDirectory: customSyncFolder,
                          );
                          await ApiService.confirmTransfer(file['id']);

                          setState(() {
                            pendingFiles.removeAt(index);
                            status = pendingFiles.isEmpty
                            ? "All synced up"
                            : "Found ${pendingFiles.length} pending file(s)";
                          });

                          if (!mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              behavior: SnackBarBehavior.floating,
                              backgroundColor: theme.colorScheme.primaryContainer,
                              margin: const EdgeInsets.all(16),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              content: Row(
                                children: [
                                  Icon(Icons.check_circle_rounded, color: theme.colorScheme.onPrimaryContainer, size: 20),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Text(
                                      '${file['filename']} saved.',
                                      style: TextStyle(color: theme.colorScheme.onPrimaryContainer, fontWeight: FontWeight.w500),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
