# Database Setup and Mock Data Generation

## Overview

The JobPilot system uses SQLite for development with automatic table creation and a mock data generator for testing the new Skill Bank functionality.

## Development Workflow

### 1. Fresh Database Setup

For a fresh start with the updated Skill Bank data models:

```bash
# Delete existing database (if it exists)
rm -f data/jobpilot.db

# Start the web server (creates tables automatically)
python web_server.py

# Stop the server (Ctrl+C)

# Generate comprehensive mock data
python scripts/generate_mock_data.py

# Restart the server for testing
python web_server.py
```

### 2. Database Auto-Creation

The database tables are automatically created when you start the web server because:

- `DatabaseManager.__init__()` calls `self.create_tables()`
- `create_tables()` uses `Base.metadata.create_all(self.engine)`
- All SQLAlchemy models are imported and included in the `Base` metadata

### 3. Mock Data Generation

The `generate_mock_data.py` script creates:

- **3 Sample Users** with different roles:
  - Sarah Johnson (Senior Software Engineer)
  - Michael Chen (Data Scientist)  
  - Emma Rodriguez (Product Manager)

- **Comprehensive Skill Banks** for each user:
  - 7-11 skills per user (technical + soft skills)
  - 3 work experiences with content variations
  - 2 education entries
  - 3 projects
  - 2 certifications
  - Multiple summary variations

### 4. What Gets Created

#### User Profiles
- Complete contact information (name, email, phone, location, LinkedIn, portfolio)
- Job preferences and salary expectations
- Professional bio content

#### Skill Banks
- **Skills**: Categorized by type (Technical, Soft, Framework, Platform, etc.)
- **Summary Variations**: Multiple versions with different focuses (Technical, Leadership, Results)
- **Work Experiences**: Full job history with achievements and content variations
- **Education**: Degrees with relevant coursework and honors
- **Projects**: Technical projects with descriptions and technologies used
- **Certifications**: Professional certifications with expiration tracking

#### Content Variations
Each major section (summaries, experiences) includes multiple content variations:
- **Technical Focus**: Emphasizes technical skills and achievements
- **Leadership Focus**: Highlights management and mentoring experience
- **Results Focus**: Focuses on quantifiable achievements and impact

## Files Created

### Scripts
- `scripts/generate_mock_data.py` - Main mock data generation script

### Data Models
- `app/data/mock_data_generator.py` - Mock data generator class
- `app/data/skill_bank_models.py` - Enhanced SkillBank data models
- `app/data/database.py` - Database manager with auto-table creation

### Documentation
- `docs/database_setup.md` - This documentation file

## Testing the Implementation

After running the mock data generation:

1. **Start the web server**: `python web_server.py`
2. **Navigate to**: http://localhost:8080
3. **Test Skill Bank features**:
   - Visit the Skill Bank dashboard
   - View different users' skill profiles
   - Test CRUD operations on skills, experiences, etc.
4. **Test Resume Builder integration**:
   - Use "Use from Skill Bank" toggles
   - Select content from Skill Bank
   - Verify data flows correctly

## Database Schema

The enhanced schema includes:

- **UserProfileDB**: Extended with new contact fields (city, state, linkedin_url, portfolio_url)
- **EnhancedSkillBankDB**: New comprehensive skill bank model
- **Skill Categories**: Technical, Soft, Framework, Platform, Tool, Methodology, Domain, etc.
- **Content Variations**: Flexible content variation system for different contexts

## Development Best Practices

1. **Clean Slate Testing**: Delete `data/jobpilot.db` when testing schema changes
2. **Server-First**: Always start the server first to create tables
3. **Mock Data Last**: Generate mock data after tables are created
4. **Version Control**: The `data/` directory is gitignored - database files are local only

## Production Considerations

- Mock data generation is development-only - not included in production web server
- Use environment-specific database URLs for different environments
- Implement proper migrations for production schema changes
- Consider seeding production with minimal data rather than mock data

## Troubleshooting

### Database File Not Found
```
❌ Database file not found!
```
**Solution**: Start the web server first, then stop it, then run the mock data script.

### Health Check Failed
```
❌ Database health check failed!
```
**Solution**: Ensure no other process is using the database file, or delete and recreate it.

### Import Errors
**Solution**: Ensure you're running the script from the project root directory.

## Next Steps

1. Test all Skill Bank CRUD operations with the mock data
2. Verify Resume Builder integration works with Skill Bank data
3. Test the complete end-to-end workflow from Skill Bank to Resume generation
4. Consider additional mock data scenarios as needed
