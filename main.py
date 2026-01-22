"""FastAPI server for skills-ref functionality."""

import html
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
# from fastapi.responses import JSONResponse
from pydantic import BaseModel

from errors import SkillError, ParseError
from parser import parse_frontmatter
from validator import validate_metadata

app = FastAPI(
    title="Skills Reference API",
    description="API for validating, reading, and managing Agent Skills",
    version="0.1.0"
)

# Mount the current directory as a static file server
# This allows page.html to be served
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/", include_in_schema=False)
async def read_root():
    """Serve the index.html file."""
    return FileResponse('page.html')


class ValidationTextRequest(BaseModel):
    """Request model for skill text validation."""
    content: str
    
    class Config:
        # Limit request size to 1MB
        max_anystr_length = 1_000_000


class ValidationResponse(BaseModel):
    """Response model for skill validation."""
    valid: bool
    problems: Optional[List[str]] = None


class PropertiesResponse(BaseModel):
    """Response model for skill properties."""
    name: str
    description: str


class PromptResponse(BaseModel):
    """Response model for prompt generation."""
    prompt: str

@app.post("/validate/text", response_model=ValidationResponse)
async def validate_skill_text(request: ValidationTextRequest):
    """
    Validate skill markdown text content directly.
    
    Args:
        request: ValidationTextRequest containing the MD text content (max 1MB)
        
    Returns:
        ValidationResponse with validation results
        
    Example:
        POST /validate/text
        {
            "content": "---\\nname: my-skill\\ndescription: A skill\\n---\\n# Instructions\\n..."
        }
    """
    try:
        # Validate content size
        content_size = len(request.content.encode('utf-8'))
        if content_size > 1_000_000:
            raise HTTPException(
                status_code=413,
                detail=f"Content size {content_size} bytes exceeds 1MB limit"
            )
        
        # Parse frontmatter and validate metadata
        # This matches the code from validator.py lines 171-175
        try:
            metadata, _ = parse_frontmatter(request.content)
        except ParseError as e:
            return ValidationResponse(
                valid=False,
                problems=[str(e)]
            )
        
        # Validate the metadata (without skill_dir check since we don't have a directory)
        problems = validate_metadata(metadata, skill_dir=None)
        
        return ValidationResponse(
            valid=len(problems) == 0,
            problems=problems if problems else None
        )
        
    except HTTPException:
        raise
    except SkillError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/properties/text", response_model=PropertiesResponse)
async def get_properties_from_text(request: ValidationTextRequest):
    """
    Read properties from skill markdown text content directly.
    
    Args:
        request: ValidationTextRequest containing the MD text content (max 1MB)
        
    Returns:
        PropertiesResponse with skill name and description
        
    Example:
        POST /properties/text
        {
            "content": "---\\nname: my-skill\\ndescription: A skill\\n---\\n# Instructions\\n..."
        }
    """
    try:
        # Validate content size
        content_size = len(request.content.encode('utf-8'))
        if content_size > 1_000_000:
            raise HTTPException(
                status_code=413,
                detail=f"Content size {content_size} bytes exceeds 1MB limit"
            )
        
        # Parse frontmatter directly from content
        # This matches the code from parser.py lines 89-90
        metadata, _ = parse_frontmatter(request.content)
        
        # Validate required fields
        if "name" not in metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing required field in frontmatter: name"
            )
        if "description" not in metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing required field in frontmatter: description"
            )
        
        name = metadata["name"]
        description = metadata["description"]
        
        if not isinstance(name, str) or not name.strip():
            raise HTTPException(
                status_code=400,
                detail="Field 'name' must be a non-empty string"
            )
        if not isinstance(description, str) or not description.strip():
            raise HTTPException(
                status_code=400,
                detail="Field 'description' must be a non-empty string"
            )
        
        return PropertiesResponse(
            name=name.strip(),
            description=description.strip()
        )
        
    except HTTPException:
        raise
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SkillError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/prompt/text", response_model=PromptResponse)
async def generate_prompt_text(request: ValidationTextRequest):
    """
    Generate agent prompt XML from skill markdown text content directly.
    
    Args:
        request: ValidationTextRequest containing the MD text content (max 1MB)
        
    Returns:
        PromptResponse with generated XML prompt
        
    Example:
        POST /prompt/text
        {
            "content": "---\\nname: my-skill\\ndescription: A skill\\n---\\n# Instructions\\n..."
        }
    """
    try:
        # Validate content size
        content_size = len(request.content.encode('utf-8'))
        if content_size > 1_000_000:
            raise HTTPException(
                status_code=413,
                detail=f"Content size {content_size} bytes exceeds 1MB limit"
            )
        
        # Parse frontmatter directly from content
        metadata, _ = parse_frontmatter(request.content)
        
        # Validate required fields
        if "name" not in metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing required field in frontmatter: name"
            )
        if "description" not in metadata:
            raise HTTPException(
                status_code=400,
                detail="Missing required field in frontmatter: description"
            )
        
        name = metadata["name"]
        description = metadata["description"]
        
        # Construct XML
        lines = ["<available_skills>", "<skill>"]
        
        lines.append("<name>")
        lines.append(html.escape(name.strip()))
        lines.append("</name>")
        
        lines.append("<description>")
        lines.append(html.escape(description.strip()))
        lines.append("</description>")
        
        lines.append("<location>")
        lines.append("memory")  # Placeholder for text-based content
        lines.append("</location>")
        
        lines.append("</skill>")
        lines.append("</available_skills>")
        
        return PromptResponse(prompt="\n".join(lines))
        
    except HTTPException:
        raise
    except ParseError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9900)
