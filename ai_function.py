from schema import UserBioData

async def generate_user_story(user: UserBioData) -> str:
    """Generate a user story based on the provided user bio data"""
    try:
        story = f"{user.first_name} {user.last_name} is a {user.age}-year-old "
        if user.gender:
            story += f"{user.gender.lower()} "
        story += f"from {user.location}. "
        
        if user.occupation:
            story += f"They work as a {user.occupation}. "
        
        if user.hobbies:
            hobbies_formatted = ", ".join(user.hobbies)
            story += f"Their hobbies include {hobbies_formatted}. "
        
        if user.languages_spoken:
            languages_formatted = ", ".join(user.languages_spoken)
            story += f"They speak the following languages: {languages_formatted}. "
        
        if user.social_links:
            links = ", ".join(f"{link.platform} ({link.url})" for link in user.social_links)
            story += f"You can find them on: {links}. "
        
        return story.strip()
    
    except Exception as e:
        raise ValueError(f"Error generating user story: {e}")
