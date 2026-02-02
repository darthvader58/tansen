import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../providers/user_provider.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  // Notification preferences
  bool _practiceReminders = true;
  bool _achievementNotifications = true;
  bool _newSongsNotifications = true;
  bool _weeklyProgress = true;
  bool _communityUpdates = false;
  bool _emailNotifications = true;
  bool _pushNotifications = true;
  bool _soundEnabled = true;
  
  TimeOfDay _reminderTime = const TimeOfDay(hour: 18, minute: 0);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
      ),
      body: ListView(
        children: [
          // Practice Reminders Section
          _buildSectionHeader('Practice Reminders'),
          SwitchListTile(
            secondary: const Icon(Icons.alarm),
            title: const Text('Daily Practice Reminders'),
            subtitle: const Text('Get reminded to practice every day'),
            value: _practiceReminders,
            onChanged: (value) {
              setState(() {
                _practiceReminders = value;
              });
            },
          ),
          if (_practiceReminders)
            ListTile(
              leading: const SizedBox(width: 40),
              title: const Text('Reminder Time'),
              subtitle: Text(_formatTime(_reminderTime)),
              trailing: const Icon(Icons.chevron_right),
              onTap: _selectReminderTime,
            ),
          
          const Divider(),
          
          // Progress & Achievements Section
          _buildSectionHeader('Progress & Achievements'),
          SwitchListTile(
            secondary: const Icon(Icons.emoji_events),
            title: const Text('Achievement Notifications'),
            subtitle: const Text('Celebrate your milestones'),
            value: _achievementNotifications,
            onChanged: (value) {
              setState(() {
                _achievementNotifications = value;
              });
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.trending_up),
            title: const Text('Weekly Progress Report'),
            subtitle: const Text('Get a summary of your practice every week'),
            value: _weeklyProgress,
            onChanged: (value) {
              setState(() {
                _weeklyProgress = value;
              });
            },
          ),
          
          const Divider(),
          
          // Content Updates Section
          _buildSectionHeader('Content Updates'),
          SwitchListTile(
            secondary: const Icon(Icons.library_music),
            title: const Text('New Songs'),
            subtitle: const Text('Get notified when new songs are added'),
            value: _newSongsNotifications,
            onChanged: (value) {
              setState(() {
                _newSongsNotifications = value;
              });
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.people),
            title: const Text('Community Updates'),
            subtitle: const Text('News and updates from the community'),
            value: _communityUpdates,
            onChanged: (value) {
              setState(() {
                _communityUpdates = value;
              });
            },
          ),
          
          const Divider(),
          
          // Notification Channels Section
          _buildSectionHeader('Notification Channels'),
          SwitchListTile(
            secondary: const Icon(Icons.notifications),
            title: const Text('Push Notifications'),
            subtitle: const Text('Receive notifications on this device'),
            value: _pushNotifications,
            onChanged: (value) {
              setState(() {
                _pushNotifications = value;
              });
            },
          ),
          SwitchListTile(
            secondary: const Icon(Icons.email),
            title: const Text('Email Notifications'),
            subtitle: const Text('Receive notifications via email'),
            value: _emailNotifications,
            onChanged: (value) {
              setState(() {
                _emailNotifications = value;
              });
            },
          ),
          
          const Divider(),
          
          // Sound & Vibration Section
          _buildSectionHeader('Sound & Vibration'),
          SwitchListTile(
            secondary: const Icon(Icons.volume_up),
            title: const Text('Notification Sound'),
            subtitle: const Text('Play sound for notifications'),
            value: _soundEnabled,
            onChanged: (value) {
              setState(() {
                _soundEnabled = value;
              });
            },
          ),
          
          const SizedBox(height: 24),
          
          // Save Button
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: ElevatedButton(
              onPressed: _saveNotificationSettings,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
              ),
              child: const Text('Save Preferences'),
            ),
          ),
          
          // Test Notification Button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: OutlinedButton.icon(
              onPressed: _sendTestNotification,
              icon: const Icon(Icons.send),
              label: const Text('Send Test Notification'),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
              ),
            ),
          ),
          
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.w600,
          color: AppTheme.primaryBlue,
        ),
      ),
    );
  }

  String _formatTime(TimeOfDay time) {
    final hour = time.hourOfPeriod;
    final minute = time.minute.toString().padLeft(2, '0');
    final period = time.period == DayPeriod.am ? 'AM' : 'PM';
    return '$hour:$minute $period';
  }

  Future<void> _selectReminderTime() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _reminderTime,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: const ColorScheme.light(
              primary: AppTheme.primaryBlue,
            ),
          ),
          child: child!,
        );
      },
    );
    
    if (picked != null && picked != _reminderTime) {
      setState(() {
        _reminderTime = picked;
      });
    }
  }

  Future<void> _saveNotificationSettings() async {
    final userProvider = Provider.of<UserProvider>(context, listen: false);
    
    // Show loading indicator
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const Center(
        child: CircularProgressIndicator(),
      ),
    );
    
    // Prepare notification preferences
    final settings = {
      'practice_reminders': _practiceReminders,
      'reminder_time': '${_reminderTime.hour}:${_reminderTime.minute}',
      'achievement_notifications': _achievementNotifications,
      'new_songs_notifications': _newSongsNotifications,
      'weekly_progress': _weeklyProgress,
      'community_updates': _communityUpdates,
      'email_notifications': _emailNotifications,
      'push_notifications': _pushNotifications,
      'sound_enabled': _soundEnabled,
    };
    
    // Save to backend
    final success = await userProvider.updateNotificationPreferences(settings);
    
    // Hide loading indicator
    if (mounted) Navigator.pop(context);
    
    if (success) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Notification preferences saved!'),
            backgroundColor: AppTheme.successGreen,
          ),
        );
      }
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(userProvider.error ?? 'Failed to save preferences'),
            backgroundColor: AppTheme.errorRed,
          ),
        );
      }
    }
  }

  void _sendTestNotification() {
    // TODO: Trigger a test notification
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const Icon(Icons.notifications_active, color: AppTheme.white),
            const SizedBox(width: 12),
            const Expanded(
              child: Text('Test notification sent! Check your notifications.'),
            ),
          ],
        ),
        backgroundColor: AppTheme.primaryBlue,
        duration: const Duration(seconds: 3),
      ),
    );
  }
}
