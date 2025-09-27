from schema import UserBioData
import google.generativeai as genai
import json
from pydantic import ValidationError
from typing import Optional
from schema import Story


genai.configure(api_key="")


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

def generate_story_from_input(user_data: UserBioData) -> Optional[Story]:
    """
    Generates a story using the first Gemini model and validates it with Pydantic.

    Args:
        user_data: A Pydantic object containing detailed user information.

    Returns:
        A validated Story object, or None if an error occurs.
    """
    print("🤖 Calling Gemini to generate a story based on detailed user data...")
    
    # Define the generation config for JSON output
    generation_config = {
        "response_mime_type": "application/json",
    }
    
    prompt = f"""
    Based on the following user data, create a short, imaginative story.
    Pick a few interesting details from the data (like their occupation, a hobby, and an address) to build a narrative.
    The story should be heartwarming and inspirational. The main character's name MUST be {user_data.preferred_name or user_data.first_name}.

    User Data (JSON):
    {user_data.model_dump_json(indent=2)}
    """
    
    try:
        story_model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config=generation_config
        )
        
        # We pass the schema to the model to guide its output.
        response = story_model.generate_content(
            [prompt],
            generation_config=genai.types.GenerationConfig(
                response_schema=Story
            )
        )

        # The response text should be a JSON string that matches our Story model
        response_json = json.loads(response.text)
        
        print("✅ Story generated. Now validating with Pydantic...")
        
        # Use Pydantic to validate the JSON from the model.
        # This will raise a ValidationError if the data doesn't match the schema.
        validated_story = Story.model_validate(response_json)
        
        print("✅ Pydantic validation successful!")
        return validated_story

    except ValidationError as e:
        print(f"🛑 Pydantic Validation Error: The model's response did not match the required format.\n{e}")
        return None
    except Exception as e:
        print(f"🛑 An unexpected error occurred during story generation: {e}")
        return None


def translate_story_to_swahili(story: Story) -> Optional[str]:
    """
    Translates the body of the story to Swahili using a second Gemini model.

    Args:
        story: The validated Story object.

    Returns:
        The translated story text, or None if an error occurs.
    """
    print("\n🤖 Calling Gemini again to translate the story to Swahili...")
    
    translation_model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"Please translate the following story into Swahili:\n\n---\n\n{story.story_body}"
    
    try:
        response = translation_model.generate_content(prompt)
        print("✅ Translation complete!")
        return response.text
    except Exception as e:
        print(f"🛑 An unexpected error occurred during translation: {e}")
        return None

