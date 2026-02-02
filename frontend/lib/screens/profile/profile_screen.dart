import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/theme_service.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // Profile Header
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      AppTheme.primaryBlue,
                      isDark ? AppTheme.spotifyBlack : AppTheme.white,
                    ],
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      CircleAvatar(
                        radius: 50,
                        backgroundColor: AppTheme.white,
                        child: const Icon(
                          Icons.person,
                          size: 50,
                          color: AppTheme.primaryBlue,
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text(
                        'Music Learner',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.white,
                        ),
                      ),
                      const Text(
                        'Intermediate • Piano',
                        style: TextStyle(
                          fontSize: 14,
                          color: AppTheme.paleBlue,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          SliverPadding(
            padding: const EdgeInsets.all(24.0),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                // Stats Overview
                _buildStatsSection(),
                
                const SizedBox(height: 32),
                
                // Practice Progress
                _buildSectionHeader('Practice Progress', 'Your learning journey'),
                const SizedBox(height: 16),
                _buildProgressChart(),
                
                const SizedBox(height: 32),
                
                // Instruments Practiced
                _buildSectionHeader('Instruments', 'What you\'ve been practicing'),
                const SizedBox(height: 16),
                _buildInstrumentsGrid(),
                
                const SizedBox(height: 32),
                
                // Recent Activity
                _buildSectionHeader('Recent Activity', 'Your practice sessions'),
                const SizedBox(height: 16),
                _buildRecentActivity(),
                
                const SizedBox(height: 32),
                
                // AI Teaching Sessions
                _buildSectionHeader('AI Teaching Sessions', 'Get feedback on your playing'),
                const SizedBox(height: 16),
                _buildAITeachingCard(context),
                
                const SizedBox(height: 32),
                
                // Settings
                _buildSectionHeader('Settings', 'Customize your experience'),
                const SizedBox(height: 16),
                _buildSettingsSection(context),
                
                const SizedBox(height: 100),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsSection() {
    return Row(
      children: [
        Expanded(child: _buildStatCard('127', 'Practice Hours', Icons.access_time, AppTheme.primaryBlue)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('23', 'Songs Learned', Icons.music_note, AppTheme.successGreen)),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard('15', 'Day Streak', Icons.local_fire_department, AppTheme.accentOrange)),
      ],
    );
  }

  Widget _buildStatCard(String value, String label, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: AppTheme.mediumGray,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: const TextStyle(
            fontSize: 14,
            color: AppTheme.mediumGray,
          ),
        ),
      ],
    );
  }

  Widget _buildProgressChart() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Last 7 Days',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 20),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                _buildBarChart('Mon', 45, 100),
                _buildBarChart('Tue', 60, 100),
                _buildBarChart('Wed', 30, 100),
                _buildBarChart('Thu', 75, 100),
                _buildBarChart('Fri', 50, 100),
                _buildBarChart('Sat', 90, 100),
                _buildBarChart('Sun', 65, 100),
              ],
            ),
            const SizedBox(height: 16),
            const Text(
              'Average: 59 minutes/day',
              style: TextStyle(
                fontSize: 12,
                color: AppTheme.mediumGray,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBarChart(String label, double value, double max) {
    final height = (value / max) * 120;
    return Column(
      children: [
        Container(
          width: 32,
          height: height,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [AppTheme.primaryBlue, AppTheme.darkBlue],
            ),
            borderRadius: BorderRadius.circular(4),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            color: AppTheme.mediumGray,
          ),
        ),
      ],
    );
  }

  Widget _buildInstrumentsGrid() {
    final instruments = [
      {'name': 'Piano', 'hours': 45, 'icon': Icons.piano, 'color': AppTheme.primaryBlue},
      {'name': 'Guitar', 'hours': 32, 'icon': Icons.music_note, 'color': AppTheme.successGreen},
      {'name': 'Vocals', 'hours': 28, 'icon': Icons.mic, 'color': AppTheme.accentOrange},
      {'name': 'Drums', 'hours': 15, 'icon': Icons.album, 'color': AppTheme.errorRed},
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.5,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: instruments.length,
      itemBuilder: (context, index) {
        final instrument = instruments[index];
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: (instrument['color'] as Color).withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        instrument['icon'] as IconData,
                        color: instrument['color'] as Color,
                        size: 24,
                      ),
                    ),
                    Text(
                      '${instrument['hours']}h',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                Text(
                  instrument['name'] as String,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildRecentActivity() {
    final activities = [
      {'song': 'Imagine', 'artist': 'John Lennon', 'duration': '45 min', 'date': 'Today'},
      {'song': 'Let It Be', 'artist': 'The Beatles', 'duration': '30 min', 'date': 'Yesterday'},
      {'song': 'Wonderwall', 'artist': 'Oasis', 'duration': '25 min', 'date': '2 days ago'},
    ];

    return Card(
      child: Column(
        children: activities.map((activity) {
          return ListTile(
            leading: Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.lightBlue, AppTheme.primaryBlue],
                ),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.music_note, color: AppTheme.white),
            ),
            title: Text(
              activity['song']!,
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            subtitle: Text('${activity['artist']} • ${activity['duration']}'),
            trailing: Text(
              activity['date']!,
              style: const TextStyle(
                fontSize: 12,
                color: AppTheme.mediumGray,
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildAITeachingCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppTheme.primaryBlue, AppTheme.darkBlue],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.psychology,
                    color: AppTheme.white,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'AI Practice Coach',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 4),
                      Text(
                        'Get real-time feedback on your playing',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppTheme.mediumGray,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),
            const Text(
              'Record yourself playing and get instant AI-powered feedback on:',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 12),
            _buildFeatureItem(Icons.music_note, 'Note accuracy'),
            _buildFeatureItem(Icons.speed, 'Tempo consistency'),
            _buildFeatureItem(Icons.timeline, 'Rhythm precision'),
            _buildFeatureItem(Icons.trending_up, 'Improvement suggestions'),
            const SizedBox(height: 20),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const AITeachingScreen(),
                    ),
                  );
                },
                icon: const Icon(Icons.mic),
                label: const Text('Start Practice Session'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 16, color: AppTheme.primaryBlue),
          const SizedBox(width: 8),
          Text(text, style: const TextStyle(fontSize: 13)),
        ],
      ),
    );
  }

  Widget _buildSettingsSection(BuildContext context) {
    return Card(
      child: Column(
        children: [
          Consumer<ThemeService>(
            builder: (context, themeService, _) {
              return SwitchListTile(
                secondary: Icon(
                  themeService.isDarkMode ? Icons.dark_mode : Icons.light_mode,
                ),
                title: const Text('Dark Mode'),
                subtitle: const Text('Switch between light and dark theme'),
                value: themeService.isDarkMode,
                onChanged: (_) => themeService.toggleTheme(),
              );
            },
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.person),
            title: const Text('Edit Profile'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.notifications),
            title: const Text('Notifications'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {},
          ),
          const Divider(height: 1),
          ListTile(
            leading: const Icon(Icons.logout, color: AppTheme.errorRed),
            title: const Text('Sign Out', style: TextStyle(color: AppTheme.errorRed)),
            onTap: () {},
          ),
        ],
      ),
    );
  }
}

// AI Teaching Screen
class AITeachingScreen extends StatefulWidget {
  const AITeachingScreen({super.key});

  @override
  State<AITeachingScreen> createState() => _AITeachingScreenState();
}

class _AITeachingScreenState extends State<AITeachingScreen> {
  bool _isRecording = false;
  bool _isAnalyzing = false;
  bool _hasResults = false;
  
  Map<String, dynamic>? _analysisResults;

  @override
  Widget build(BuildContext context) {
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
                    ListTile(
                      leading: Container(
                        width: 48,
                        height: 48,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [AppTheme.lightBlue, AppTheme.primaryBlue],
                          ),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.music_note, color: AppTheme.white),
                      ),
                      title: const Text('Imagine'),
                      subtitle: const Text('John Lennon • Piano'),
                      trailing: const Icon(Icons.chevron_right),
                      onTap: () {},
                    ),
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
                        onTap: _toggleRecording,
                        child: Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: LinearGradient(
                              colors: _isRecording
                                  ? [AppTheme.errorRed, AppTheme.errorRed.withValues(alpha: 0.7)]
                                  : [AppTheme.primaryBlue, AppTheme.darkBlue],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: (_isRecording ? AppTheme.errorRed : AppTheme.primaryBlue)
                                    .withValues(alpha: 0.3),
                                blurRadius: 20,
                                spreadRadius: 5,
                              ),
                            ],
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
                        _isRecording ? 'Recording... Tap to stop' : 'Tap to start recording',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      
                      if (_isAnalyzing) ...[
                        const SizedBox(height: 32),
                        const CircularProgressIndicator(),
                        const SizedBox(height: 16),
                        const Text('Analyzing your performance...'),
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

  void _toggleRecording() {
    setState(() {
      if (_isRecording) {
        _isRecording = false;
        _isAnalyzing = true;
        
        // Simulate analysis
        Future.delayed(const Duration(seconds: 3), () {
          setState(() {
            _isAnalyzing = false;
            _hasResults = true;
            _analysisResults = {
              'overall_score': 85,
              'note_accuracy': 88,
              'tempo_consistency': 82,
              'rhythm_precision': 85,
              'feedback': [
                'Great job! Your note accuracy is excellent.',
                'Try to maintain a more consistent tempo in measures 12-16.',
                'Your rhythm is solid, keep practicing!',
              ],
              'improvements': [
                {'measure': '12-16', 'issue': 'Tempo variation', 'suggestion': 'Use a metronome'},
                {'measure': '24', 'issue': 'Missed note', 'suggestion': 'Practice this section slowly'},
              ],
            };
          });
        });
      } else {
        _isRecording = true;
      }
    });
  }

  Widget _buildAnalysisResults() {
    final score = _analysisResults!['overall_score'] as int;
    
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
              const Text(
                'Overall Score',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // Detailed Metrics
        _buildMetricBar('Note Accuracy', _analysisResults!['note_accuracy'] as int),
        const SizedBox(height: 12),
        _buildMetricBar('Tempo Consistency', _analysisResults!['tempo_consistency'] as int),
        const SizedBox(height: 12),
        _buildMetricBar('Rhythm Precision', _analysisResults!['rhythm_precision'] as int),
        
        const SizedBox(height: 32),
        
        // Feedback
        const Text(
          'Feedback',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...(_analysisResults!['feedback'] as List).map((feedback) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.check_circle, color: AppTheme.successGreen, size: 20),
                const SizedBox(width: 8),
                Expanded(child: Text(feedback as String)),
              ],
            ),
          );
        }),
        
        const SizedBox(height: 24),
        
        // Improvements
        const Text(
          'Areas to Improve',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...(_analysisResults!['improvements'] as List).map((improvement) {
          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.warning_amber, color: AppTheme.accentOrange, size: 20),
                      const SizedBox(width: 8),
                      Text(
                        'Measure ${improvement['measure']}',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text('Issue: ${improvement['issue']}'),
                  const SizedBox(height: 4),
                  Text(
                    'Suggestion: ${improvement['suggestion']}',
                    style: const TextStyle(color: AppTheme.primaryBlue),
                  ),
                ],
              ),
            ),
          );
        }),
        
        const SizedBox(height: 24),
        
        // Action Buttons
        Row(
          children: [
            Expanded(
              child: OutlinedButton(
                onPressed: () {
                  setState(() {
                    _hasResults = false;
                    _analysisResults = null;
                  });
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
