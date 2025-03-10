# GitHub Integration Guide for Replit

## Setting Up GitHub Integration

1. **Connect Your GitHub Account**
   - Click on your Replit profile icon
   - Go to 'Connected Services'
   - Click 'Connect' next to GitHub
   - Authorize Replit to access your GitHub account

2. **Initialize Git Repository**
   - Open the "Tools" panel in Replit (left sidebar)
   - Click on "Git"
   - Click "Create a Git repo"
   - This will initialize a new Git repository in your Repl

## Common Git Operations in Replit

### Committing Changes
1. Open the Git panel in Tools
2. You'll see all changed files listed
3. Enter a commit message describing your changes
4. Click "Commit all changes"

### Pushing to GitHub
1. After committing, click "Push" in the Git panel
2. First time pushing:
   - Click "Create a GitHub repository"
   - Choose a repository name
   - Select public/private
   - Click "Create repository"

### Pulling Updates
1. Open the Git panel
2. Click "Pull" to get latest changes
3. Resolve any conflicts if they appear

### Working with Branches
1. Create new branch:
   - Click "main" in Git panel
   - Select "Create new branch"
   - Enter branch name
   - Click "Create"

2. Switch branches:
   - Click current branch name
   - Select desired branch

### Quick Commands
You can also use the Shell panel in Replit:
```bash
# Check status
git status

# Add files
git add .

# Commit changes
git commit -m "Your commit message"

# Push changes
git push origin main

# Pull updates
git pull origin main

# Create and switch to new branch
git checkout -b feature-branch
```

## Best Practices

1. **Regular Commits**
   - Make small, focused commits
   - Write clear commit messages
   - Commit related changes together

2. **Pull Before Push**
   - Always pull latest changes before pushing
   - This helps avoid merge conflicts

3. **Branch Strategy**
   - Create feature branches for new features
   - Use `main` branch for stable code
   - Delete branches after merging

4. **Gitignore**
   - Use `.gitignore` to exclude unnecessary files
   - Replit already added common ignore patterns

## Troubleshooting

1. **Authentication Issues**
   - Reconnect GitHub in Connected Services
   - Check if your GitHub token is valid

2. **Merge Conflicts**
   - Pull latest changes before making modifications
   - Use Replit's built-in merge conflict resolver
   - When in doubt, make a backup branch

3. **Push Rejected**
   - Pull latest changes first
   - Resolve any conflicts
   - Try pushing again

## Need Help?

- Check Replit Docs for detailed Git integration guide
- Visit GitHub Help for general Git questions
- Ask the community in Replit's Discord
