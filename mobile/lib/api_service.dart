import 'dart:convert';
import 'package:http/http.dart' as http;

const String relayUrl = "https://datasynk.onrender.com";
const String myDeviceId = "phone-001";

class ApiService {
  static Future<List<dynamic>> pollPending() async {
    final url = "$relayUrl/poll/$myDeviceId";
    print("Polling: $url");
    final response = await http.get(Uri.parse(url));
    print("Response: ${response.statusCode} ${response.body}");
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }

  static Future<void> confirmTransfer(int transferId) async {
    await http.post(Uri.parse("$relayUrl/confirm/$transferId"));
  }

  static Future<void> notifyRelay({
    required String targetDevice,
    required String fileKey,
    required String filename,
  }) async {
    await http.post(
      Uri.parse("$relayUrl/notify"),
      body: {
        "target_device": targetDevice,
        "file_key": fileKey,
        "filename": filename,
      },
    );
  }
}
