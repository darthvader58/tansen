import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/theme/app_theme.dart';
import '../../core/services/theme_service.dart';
import '../../providers/song_provider.dart';
import '../../models/song.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Scaffold(
      body: Row(
        children: [
          // Spotify-style sidebar (only on larger screens)
          if (MediaQuery.of(context).size.width > 768)
            _buildSidebar(context, isDark),
          
          // Main content
          Expanded(
            child: _buildMainContent(),
          ),
        ],
      ),
      // Bottom nav for mobile
      bottomNavigationBar: MediaQuery.of(context).size.width <= 768
          ? _buildBottomNav()
          : null,
    );
  }

  Widget _buildSidebar(BuildContext context, bool isDark) {
    return Container(
      width: 240,
      color: isDark ? AppTheme.spotifyBlack : AppTheme.white,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Logo
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Row(
              children: [
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppTheme.primaryBlue, AppTheme.darkBlue],
                    ),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Icon(
                    Icons.music_note,
                    color: AppTheme.white,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Text(
                  'Tansen',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
              ],
            ),
          ),
          
          // Navigation items
          _buildNavItem(Icons.home, 'Home', 0, isDark),
          _buildNavItem(Icons.search, 'Search', 1, isDark),
          _buildNavItem(Icons.library_music, 'Your Library', 2, isDark),
          
          const SizedBox(height: 24),
          
          _buildNavItem(Icons.add_circle_outline, 'Create Transcription', 3, isDark),
          _buildNavItem(Icons.favorite_border, 'Liked Songs', 4, isDark),
          
          const Spacer(),
          
          // Theme toggle
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Consumer<ThemeService>(
              builder: (context, themeService, _) {
                return ListTile(
                  leading: Icon(
                    themeService.isDarkMode ? Icons.light_mode : Icons.dark_mode,
                    color: isDark ? AppTheme.spotifyLightGray : AppTheme.mediumGray,
                  ),
                  title: Text(
                    themeService.isDarkMode ? 'Light Mode' : 'Dark Mode',
                    style: TextStyle(
                      fontSize: 14,
                      color: isDark ? AppTheme.spotifyLightGray : AppTheme.mediumGray,
                    ),
                  ),
                  onTap: () => themeService.toggleTheme(),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(IconData icon, String label, int index, bool isDark) {
    final isSelected = _selectedIndex == index;
    
    return ListTile(
      leading: Icon(
        icon,
        color: isSelected
            ? AppTheme.primaryBlue
            : (isDark ? AppTheme.spotifyLightGray : AppTheme.mediumGray),
      ),
      title: Text(
        label,
        style: TextStyle(
          fontSize: 14,
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          color: isSelected
              ? AppTheme.primaryBlue
              : (isDark ? AppTheme.spotifyLightGray : AppTheme.mediumGray),
        ),
      ),
      selected: isSelected,
      selectedTileColor: isDark
          ? AppTheme.spotifyGray.withValues(alpha: 0.3)
          : AppTheme.lightGray,
      onTap: () {
        setState(() {
          _selectedIndex = index;
        });
      },
    );
  }

  Widget _buildMainContent() {
    switch (_selectedIndex) {
      case 0:
        return const HomeTab();
      case 1:
        return const SearchTab();
      case 2:
        return const LibraryTab();
      case 3:
        return const TranscribeTab();
      case 4:
        return const LikedSongsTab();
      default:
        return const HomeTab();
    }
  }

  Widget _buildBottomNav() {
    return BottomNavigationBar(
      currentIndex: _selectedIndex > 4 ? 0 : _selectedIndex,
      onTap: (index) {
        setState(() {
          _selectedIndex = index;
        });
      },
      type: BottomNavigationBarType.fixed,
      items: const [
        BottomNavigationBarItem(
          icon: Icon(Icons.home),
          label: 'Home',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.search),
          label: 'Search',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.library_music),
          label: 'Library',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.add_circle),
          label: 'Create',
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.favorite),
          label: 'Liked',
        ),
      ],
    );
  }
}

class HomeTab extends StatelessWidget {
  const HomeTab({super.key});

  @override
  Widget build(BuildContext context) {
    final songProvider = Provider.of<SongProvider>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return CustomScrollView(
      slivers: [
        // Spotify-style gradient header
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
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      _getGreeting(),
                      style: Theme.of(context).textTheme.displaySmall?.copyWith(
                            color: AppTheme.white,
                            fontWeight: FontWeight.bold,
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
              // Quick access cards (Spotify-style)
              _buildQuickAccessSection(context, songProvider),
              
              const SizedBox(height: 40),
              
              // Made for you
              _buildSectionHeader(context, 'Made For You', 'Your personalized picks'),
              const SizedBox(height: 16),
              _buildSongGrid(songProvider.songs.take(6).toList()),
              
              const SizedBox(height: 40),
              
              // Recently played
              _buildSectionHeader(context, 'Recently Played', 'Jump back in'),
              const SizedBox(height: 16),
              _buildHorizontalSongList(songProvider.songs.take(5).toList()),
              
              const SizedBox(height: 40),
              
              // Popular
              _buildSectionHeader(context, 'Popular Right Now', 'Trending in the community'),
              const SizedBox(height: 16),
              _buildHorizontalSongList(songProvider.songs.skip(5).take(5).toList()),
              
              const SizedBox(height: 100),
            ]),
          ),
        ),
      ],
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  }

  Widget _buildQuickAccessSection(BuildContext context, SongProvider songProvider) {
    final songs = songProvider.songs.take(6).toList();
    
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        childAspectRatio: 3,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: songs.length,
      itemBuilder: (context, index) {
        return _buildQuickAccessCard(songs[index]);
      },
    );
  }

  Widget _buildQuickAccessCard(Song song) {
    return Card(
      child: InkWell(
        onTap: () {},
        child: Row(
          children: [
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppTheme.lightBlue, AppTheme.primaryBlue],
                ),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(8),
                  bottomLeft: Radius.circular(8),
                ),
              ),
              child: const Icon(Icons.music_note, color: AppTheme.white),
            ),
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                child: Text(
                  song.title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }

  Widget _buildSongGrid(List<Song> songs) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        childAspectRatio: 0.7,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: songs.length,
      itemBuilder: (context, index) {
        return _buildSongCard(songs[index]);
      },
    );
  }

  Widget _buildHorizontalSongList(List<Song> songs) {
    return SizedBox(
      height: 240,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        itemCount: songs.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: EdgeInsets.only(right: index < songs.length - 1 ? 16 : 0),
            child: SizedBox(
              width: 160,
              child: _buildSongCard(songs[index]),
            ),
          );
        },
      ),
    );
  }

  Widget _buildSongCard(Song song) {
    return Card(
      child: InkWell(
        onTap: () {},
        borderRadius: BorderRadius.circular(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Album art
            AspectRatio(
              aspectRatio: 1,
              child: Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.lightBlue, AppTheme.primaryBlue],
                  ),
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(8),
                  ),
                ),
                child: const Center(
                  child: Icon(
                    Icons.music_note,
                    size: 48,
                    color: AppTheme.white,
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    song.title,
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    song.artist,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.mediumGray,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// Placeholder tabs
class SearchTab extends StatelessWidget {
  const SearchTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Search',
              style: Theme.of(context).textTheme.displaySmall,
            ),
            const SizedBox(height: 24),
            TextField(
              decoration: const InputDecoration(
                hintText: 'What do you want to learn?',
                prefixIcon: Icon(Icons.search),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class LibraryTab extends StatelessWidget {
  const LibraryTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Your Library',
              style: Theme.of(context).textTheme.displaySmall,
            ),
            const SizedBox(height: 24),
            const Text('Your saved songs and playlists will appear here'),
          ],
        ),
      ),
    );
  }
}

class TranscribeTab extends StatelessWidget {
  const TranscribeTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(48.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 120,
                height: 120,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.primaryBlue, AppTheme.darkBlue],
                  ),
                  borderRadius: BorderRadius.circular(60),
                ),
                child: const Icon(
                  Icons.add,
                  size: 60,
                  color: AppTheme.white,
                ),
              ),
              const SizedBox(height: 32),
              Text(
                'Create Transcription',
                style: Theme.of(context).textTheme.displaySmall,
              ),
              const SizedBox(height: 16),
              Text(
                'Upload audio or paste a YouTube URL to get started',
                style: Theme.of(context).textTheme.bodyMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.upload_file),
                label: const Text('Upload Audio'),
              ),
              const SizedBox(height: 16),
              OutlinedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.link),
                label: const Text('Paste YouTube URL'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class LikedSongsTab extends StatelessWidget {
  const LikedSongsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  width: 60,
                  height: 60,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppTheme.primaryBlue, AppTheme.darkBlue],
                    ),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: const Icon(
                    Icons.favorite,
                    color: AppTheme.white,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                Text(
                  'Liked Songs',
                  style: Theme.of(context).textTheme.displaySmall,
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Text('Songs you like will appear here'),
          ],
        ),
      ),
    );
  }
}
