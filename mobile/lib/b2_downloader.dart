import 'dart:io';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

const String relayUrl = "https://datasynk.onrender.com";

class B2Downloader {
  final Dio _dio = Dio();

  Future<String?> getDownloadUrl(String fileKey) async {
    final response = await http.get(
      Uri.parse("$relayUrl/download-url/$fileKey")
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body)["url"];
    }
    return null;
  }

  // Added customDirectory parameter here
  Future<void> downloadFile({
    required String fileKey,
    required String filename,
    String? customDirectory,
  }) async {
    try {
      final downloadUrl = await getDownloadUrl(fileKey);
      if (downloadUrl == null) throw Exception("Could not get download URL");

      // Use custom folder if set, otherwise fallback to app default
      String dirPath;
      if (customDirectory != null && customDirectory.isNotEmpty) {
        dirPath = customDirectory;
      } else {
        Directory appDocDir = await getApplicationDocumentsDirectory();
        dirPath = appDocDir.path;
      }

      String savePath = '$dirPath/$filename';

      await _dio.download(
        downloadUrl,
        savePath,
        onReceiveProgress: (received, total) {
          if (total != -1) {
            print('Progress: ${((received / total) * 100).toStringAsFixed(0)}%');
          }
        },
      );

      print('Saved to: $savePath');
    } catch (e) {
      print('Download failed: $e');
    }
  }
}
