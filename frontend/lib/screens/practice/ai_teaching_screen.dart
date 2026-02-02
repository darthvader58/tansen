import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';
import '../../core/theme/app_theme.dart';
import '../../providers/practice_provider.dart';
import '../../providers/song_provider.dart';

class AITeachingScreen extends StatefulWidget {
  const AITeachingScreen({super.key});

  @override
  State<AITeachingScreen> createState() => _AITeachingScreenState();
}

class _AITeachingScreenState extends State<AITeachingScreen> {
  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isAnalyzing = false;
  bool _hasResults = false;
  String? _recordingPath;
  String? _selectedSongId;
  
  Map<String, dynamic>? _analysisResults;

  @override
  void dispose() {
    _audioRecorder.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final songProvider = Provider.of<SongProvider>(context);
    final practiceProvider = Provider.of<PracticeProvider>(context);
    
    // Listen to practice provider for analysis results
    if (practiceProvider.currentAnalysis != null && !_hasResults) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        setState(() {
          _analysisResults = practiceProvider.currentAnalysis;
          _hasResults = true;
          _isAnalyzing = false;
        });
      });
    }
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('AI Practice Coach'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Song Selection
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Select a song to practice',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),
                    if (songProvider.songs.isEmpty)
                      const Padding(
                        padding: EdgeInsets.all(16.0),
                        child: Text('Loading songs...'),
                      )
                    else
                      ...songProvider.songs.take(3).map((song) {
                        final isSelected = _selectedSongId == song.songId;
                        return ListTile(
                          leading: Container(
                            width: 48,
                            height: 48,
                            decoration: BoxDecoration(
                              gradient: LinearGradient(
                                colors: isSelected
                                    ? [AppTheme.primaryBlue, AppTheme.darkBlue]
                                    : [AppTheme.lightBlue, AppTheme.primaryBlue],
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Icon(Icons.music_note, color: AppTheme.white),
                          ),
                          title: Text(song.title),
                          subtitle: Text('${song.artist} • Piano'),
                          trailing: isSelected
                              ? const Icon(Icons.check_circle, color: AppTheme.primaryBlue)
                              : const Icon(Icons.chevron_right),
                          selected: isSelected,
                          onTap: () {
                            setState(() {
                              _selectedSongId = song.songId;
                            });
                          },
                        );
                      }),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Recording Section
            Card(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    if (!_hasResults) ...[
                      const Text(
                        'Record Your Performance',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Play along with the song and we\'ll analyze your performance',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppTheme.mediumGray,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 32),
                      
                      // Recording Button
                      GestureDetector(
                        onTap: _selectedSongId != null ? _toggleRecording : null,
                        child: Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: _selectedSongId == null
                                  ? [AppTheme.mediumGray, AppTheme.mediumGray]
                                  : _isRecording
                                      ? [AppTheme.errorRed, AppTheme.errorRed.withValues(alpha: 0.7)]
                                      : [AppTheme.primaryBlue, AppTheme.darkBlue],
                            ),
                            boxShadow: _selectedSongId != null
                                ? [
                                    BoxShadow(
                                      color: (_isRecording ? AppTheme.errorRed : AppTheme.primaryBlue)
                                          .withValues(alpha: 0.3),
                                      blurRadius: 20,
                                      spreadRadius: 5,
                                    ),
                                  ]
                                : [],
                          ),
                          child: Icon(
                            _isRecording ? Icons.stop : Icons.mic,
                            size: 60,
                            color: AppTheme.white,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      Text(
                        _selectedSongId == null
                            ? 'Select a song first'
                            : _isRecording
                                ? 'Recording... Tap to stop'
                                : 'Tap to start recording',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      
                      if (_isAnalyzing) ...[
                        const SizedBox(height: 32),
                        const CircularProgressIndicator(),
                        const SizedBox(height: 16),
                        const Text('Analyzing your performance with AI...'),
                      ],
                      
                      if (practiceProvider.error != null) ...[
                        const SizedBox(height: 16),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: AppTheme.errorRed.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.error_outline, color: AppTheme.errorRed),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  practiceProvider.error!,
                                  style: const TextStyle(color: AppTheme.errorRed),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ] else ...[
                      _buildAnalysisResults(),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      // Stop recording
      final path = await _audioRecorder.stop();
      if (path != null) {
        setState(() {
          _isRecording = false;
          _isAnalyzing = true;
          _recordingPath = path;
        });
        
        // Analyze the recording
        final practiceProvider = Provider.of<PracticeProvider>(context, listen: false);
        await practiceProvider.analyzePractice(
          audioFilePath: path,
          songId: _selectedSongId!,
          instrument: 'piano',
        );
        
        setState(() {
          _isAnalyzing = false;
        });
      }
    } else {
      // Start recording
      if (await _audioRecorder.hasPermission()) {
        // Get temporary directory
        final directory = await getTemporaryDirectory();
        final filePath = '${directory.path}/practice_${DateTime.now().millisecondsSinceEpoch}.wav';
        
        await _audioRecorder.start(
          const RecordConfig(
            encoder: AudioEncoder.wav,
            sampleRate: 44100,
            bitRate: 128000,
          ),
          path: filePath,
        );
        
        setState(() {
          _isRecording = true;
        });
      } else {
        // Show permission error
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Microphone permission is required to record'),
              backgroundColor: AppTheme.errorRed,
            ),
          );
        }
      }
    }
  }

  Widget _buildAnalysisResults() {
    if (_analysisResults == null) return const SizedBox();
    
    final score = (_analysisResults!['overall_score'] as num).toInt();
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Performance Analysis',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 24),
        
        // Overall Score
        Center(
          child: Column(
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 120,
                    height: 120,
                    child: CircularProgressIndicator(
                      value: score / 100,
                      strokeWidth: 12,
                      backgroundColor: AppTheme.lightGray,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        score >= 80 ? AppTheme.successGreen : AppTheme.accentOrange,
                      ),
                    ),
                  ),
                  Text(
                    '$score',
                    style: const TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Text(
                'Grade: ${_analysisResults!['grade']}',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Detailed Metrics
        _buildMetricBar('Pitch Accuracy', (_analysisResults!['pitch_accuracy'] as num).toInt()),
        const SizedBox(height: 12),
        _buildMetricBar('Tempo Accuracy', (_analysisResults!['tempo_accuracy'] as num).toInt()),
        const SizedBox(height: 12),
        _buildMetricBar('Rhythm Accuracy', (_analysisResults!['rhythm_accuracy'] as num).toInt()),
        
        const SizedBox(height: 32),
        
        // Suggestions
        const Text(
          'Feedback & Suggestions',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...(_analysisResults!['suggestions'] as List).map((suggestion) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lightbulb_outline, color: AppTheme.primaryBlue, size: 20),
                const SizedBox(width: 8),
                Expanded(child: Text(suggestion as String)),
              ],
            ),
          );
        }),
        
        const SizedBox(height: 24),
        
        // Tempo Feedback
        if (_analysisResults!['tempo_feedback'] != null) ...[
          const Text(
            'Tempo Analysis',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Card(
            color: AppTheme.primaryBlue.withValues(alpha: 0.1),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(_analysisResults!['tempo_feedback']['message']),
                  const SizedBox(height: 8),
                  Text(
                    'Your tempo: ${_analysisResults!['tempo_feedback']['user_tempo']} BPM',
                    style: const TextStyle(fontSize: 12),
                  ),
                  Text(
                    'Reference tempo: ${_analysisResults!['tempo_feedback']['reference_tempo']} BPM',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),
        ],
        
        // Action Buttons
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () {
                  setState(() {
                    _hasResults = false;
                    _analysisResults = null;
                    _recordingPath = null;
                  });
                  final practiceProvider = Provider.of<PracticeProvider>(context, listen: false);
                  practiceProvider.clearAnalysis();
                  practiceProvider.clearError();
                },
                child: const Text('Try Again'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                child: const Text('Done'),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildMetricBar(String label, int value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: const TextStyle(fontSize: 14)),
            Text('$value%', style: const TextStyle(fontWeight: FontWeight.w600)),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value / 100,
            minHeight: 8,
            backgroundColor: AppTheme.lightGray,
            valueColor: AlwaysStoppedAnimation<Color>(
              value >= 80 ? AppTheme.successGreen : AppTheme.accentOrange,
            ),
          ),
        ),
      ],
    );
  }
}
