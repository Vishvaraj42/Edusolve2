from pypdf import PdfReader
import os

TEXTBOOK_DIR = "textbook"
def get_textbook_path(subject, grade):
    """
    Get the path to the NCERT textbook PDF
    
    Args:
        subject: "Science" or "Maths"
        grade: 9 or 10
    
    Returns:
        Full path to PDF or None if not found
    """
    filename = f"{subject.lower()}_{grade}.pdf"
    path = os.path.join(TEXTBOOK_DIR, filename)
    
    if not os.path.exists(path):
        print(f"  PDF not found: {path}")
        return None
    
    print(f" Found textbook: {path}")
    return path


def extract_chapter_text(pdf_path, chapter_name):
    """
    Extract text from a specific chapter in the PDF
    
    Arguments:
        pdf_path: Path to the PDF file
        chapter_name: Name of the chapter to extract
    
    Returns:
        Extracted text as string
    """
    try:
        reader = PdfReader(pdf_path)
        chapter_text = ""
        in_chapter = False
        pages_read = 0
        
        for page in reader.pages:
            text = page.extract_text()
            
            # Check if this page contains the chapter we're looking for
            if chapter_name.lower() in text.lower():
                in_chapter = True
                print(f" Found chapter '{chapter_name}' in PDF")
            
            # If we're in the right chapter, collect text
            if in_chapter:
                chapter_text += text + "\n"
                pages_read += 1
                
                # Stop after collecting enough content (approx 1 chapter)
                if len(chapter_text) > 10000:  # ~10KB of text
                    break
        
        print(f" Extracted {len(chapter_text)} characters from {pages_read} pages")
        return chapter_text
    
    except Exception as e:
        print(f" Error reading PDF: {e}")
        return ""


def extract_full_pdf_text(pdf_path):
    """
    Extract all text from the entire PDF
    
    Arguments:
        pdf_path: Path to the PDF file
    
    Returns:
        All text as string
    """
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        
        print(f" Reading {len(reader.pages)} pages...")
        
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            full_text += text + "\n"
            
            # Progress indicator for large PDFs
            if (i + 1) % 10 == 0:
                print(f"   Read {i + 1} pages...")
        
        print(f" Extracted {len(full_text)} characters total")
        return full_text
    
    except Exception as e:
        print(f" Error reading PDF: {e}")
        return ""


def find_exercise_questions(pdf_text):
    """
    Find exercise/practice questions from the PDF text
    Looks for common NCERT question patterns
    
    Arguments:
        pdf_text: Text extracted from PDF
    
    Returns:
        List of question strings
    """
    lines = pdf_text.split('\n')
    questions = []
    
    # Common patterns in NCERT textbooks
    question_patterns = [
        '1.', '2.', '3.', '4.', '5.',
        'Q.1', 'Q.2', 'Q.3', 
        'Q 1', 'Q 2', 'Q 3',
        'Question 1', 'Question 2',
        '1)', '2)', '3)'
    ]
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Check if line starts with a question pattern
        if any(line_stripped.startswith(pattern) for pattern in question_patterns):
            
            # Grab the question + next 2-3 lines (multi-line questions)
            question_block = ' '.join(lines[i:i+3])
            
            # Filter out very short lines (likely headers, not questions)
            if len(question_block) > 20:
                questions.append(question_block.strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_questions = []
    for q in questions:
        if q not in seen:
            seen.add(q)
            unique_questions.append(q)
    
    # Return maximum 10 questions
    print(f" Found {len(unique_questions)} exercise questions")
    return unique_questions[:10]


# TESTING
if __name__ == "__main__":
    """Test the PDF handler functions"""
    
    print("\n" + "="*60)
    print(" PDF HANDLER TEST")
    print("="*60)
    
    # Test 1: Find textbook
    print("\n TEST 1: Find textbook")
    path = get_textbook_path("Science", 9)
    
    if path:
        # Test 2: Extract chapter
        print("\n TEST 2: Extract chapter text")
        chapter_text = extract_chapter_text(path, "Force and Laws of Motion")
        print(f"First 200 chars: {chapter_text[:200]}...")
        
        # Test 3: find questions
        print("\n TEST 3: Find exercise questions")
        questions = find_exercise_questions(chapter_text)
        for i, q in enumerate(questions[:3], 1):
            print(f"\nQ{i}: {q[:100]}...")
    
    print("\n" + "="*60)
