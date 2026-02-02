import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/theme_service.dart';
import '../../providers/practice_provider.dart';
import '../practice/ai_teaching_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final practiceProvider = Provider.of<PracticeProvider>(context);
    
    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // Profile Header
          SliverAppBar(
            expandedHeight: 220,
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
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.only(left: 24.0, right: 24.0, bottom: 20.0, top: 8.0),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.end,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircleAvatar(
                          radius: 40,
                          backgroundColor: AppTheme.white,
                          child: const Icon(
                            Icons.person,
                            size: 40,
                            color: AppTheme.primaryBlue,
                          ),
                        ),
                        const SizedBox(height: 12),
                        const Text(
                          'Music Learner',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.white,
                          ),
                        ),
                        const SizedBox(height: 4),
                        const Text(
                          'Intermediate • Piano',
                          style: TextStyle(
                            fontSize: 13,
                            color: AppTheme.paleBlue,
                          ),
                        ),
                      ],
                    ),
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
                _buildStatsSection(practiceProvider),
                
                const SizedBox(height: 32),
                
                // Practice Progress
                _buildSectionHeader('Practice Progress', 'Your learning journey'),
                const SizedBox(height: 16),
                _buildProgressChart(practiceProvider),
                
                const SizedBox(height: 32),
                
                // Instruments Practiced
                _buildSectionHeader('Instruments', 'What you\'ve been practicing'),
                const SizedBox(height: 16),
                _buildInstrumentsGrid(practiceProvider),
                
                const SizedBox(height: 32),
                
                // Recent Activity
                _buildSectionHeader('Recent Activity', 'Your practice sessions'),
                const SizedBox(height: 16),
                _buildRecentActivity(practiceProvider),
                
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

  Widget _buildStatsSection(PracticeProvider provider) {
    return Row(
      children: [
        Expanded(child: _buildStatCard(
          provider.getTotalPracticeHours().toString(),
          'Practice Hours',
          Icons.access_time,
          AppTheme.primaryBlue
        )),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard(
          provider.getSongsLearnedCount().toString(),
          'Songs Learned',
          Icons.music_note,
          AppTheme.successGreen
        )),
        const SizedBox(width: 12),
        Expanded(child: _buildStatCard(
          provider.getCurrentStreak().toString(),
          'Day Streak',
          Icons.local_fire_department,
          AppTheme.accentOrange
        )),
      ],
    );
  }

  Widget _buildStatCard(String value, String label, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 24),
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: const TextStyle(
                fontSize: 10,
                color: AppTheme.mediumGray,
              ),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
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

  Widget _buildProgressChart(PracticeProvider provider) {
    final weeklyData = provider.getWeeklyPracticeData();
    
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
              children: weeklyData.map((data) {
                return _buildBarChart(
                  data['day'] as String,
                  (data['minutes'] as int).toDouble(),
                  100,
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            Text(
              'Average: ${weeklyData.map((d) => d['minutes'] as int).reduce((a, b) => a + b) ~/ weeklyData.length} minutes/day',
              style: const TextStyle(
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

  Widget _buildInstrumentsGrid(PracticeProvider provider) {
    final instrumentData = provider.getInstrumentBreakdown();
    final instruments = instrumentData.entries.map((entry) {
      IconData icon;
      Color color;
      
      switch (entry.key.toLowerCase()) {
        case 'piano':
          icon = Icons.piano;
          color = AppTheme.primaryBlue;
          break;
        case 'guitar':
          icon = Icons.music_note;
          color = AppTheme.successGreen;
          break;
        case 'vocals':
          icon = Icons.mic;
          color = AppTheme.accentOrange;
          break;
        case 'drums':
          icon = Icons.album;
          color = AppTheme.errorRed;
          break;
        default:
          icon = Icons.music_note;
          color = AppTheme.primaryBlue;
      }
      
      return {
        'name': entry.key,
        'hours': entry.value,
        'icon': icon,
        'color': color,
      };
    }).toList();

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

  Widget _buildRecentActivity(PracticeProvider provider) {
    final sessions = provider.practiceHistory.take(3).toList();
    
    if (sessions.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Center(
            child: Column(
              children: [
                Icon(
                  Icons.music_note_outlined,
                  size: 48,
                  color: AppTheme.mediumGray.withValues(alpha: 0.5),
                ),
                const SizedBox(height: 12),
                const Text(
                  'No practice sessions yet',
                  style: TextStyle(
                    color: AppTheme.mediumGray,
                  ),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      child: Column(
        children: sessions.map((session) {
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
              session['song_title'] ?? 'Unknown Song',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            subtitle: Text(
              '${session['instrument'] ?? 'Unknown'} • Score: ${session['overall_score'] ?? 0}',
            ),
            trailing: Text(
              _formatDate(session['timestamp']),
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
  
  String _formatDate(dynamic timestamp) {
    if (timestamp == null) return 'Unknown';
    try {
      final date = DateTime.parse(timestamp.toString());
      final now = DateTime.now();
      final diff = now.difference(date);
      
      if (diff.inDays == 0) return 'Today';
      if (diff.inDays == 1) return 'Yesterday';
      if (diff.inDays < 7) return '${diff.inDays} days ago';
      return '${date.day}/${date.month}/${date.year}';
    } catch (e) {
      return 'Unknown';
    }
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
