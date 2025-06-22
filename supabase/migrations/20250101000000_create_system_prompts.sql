-- Create system_prompts table for managing AI system prompts
-- ====================================================================================

-- Create the system_prompts table
CREATE TABLE IF NOT EXISTS system_prompts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    prompt_text TEXT NOT NULL CHECK (char_length(prompt_text) > 0),
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    notes TEXT
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_system_prompts_active ON system_prompts(is_active);
CREATE INDEX IF NOT EXISTS idx_system_prompts_version ON system_prompts(version DESC);
CREATE INDEX IF NOT EXISTS idx_system_prompts_created_at ON system_prompts(created_at DESC);

-- Create RLS policies
ALTER TABLE system_prompts ENABLE ROW LEVEL SECURITY;

-- Only admins can view system prompts
CREATE POLICY "system_prompts_select_policy" ON system_prompts
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Only admins can insert system prompts
CREATE POLICY "system_prompts_insert_policy" ON system_prompts
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- Only admins can update system prompts
CREATE POLICY "system_prompts_update_policy" ON system_prompts
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = auth.uid() 
            AND users.role = 'admin'
        )
    );

-- No delete policy - we keep history

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_system_prompts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER system_prompts_updated_at_trigger
    BEFORE UPDATE ON system_prompts
    FOR EACH ROW
    EXECUTE PROCEDURE update_system_prompts_updated_at();

-- Function to ensure only one active prompt at a time
CREATE OR REPLACE FUNCTION ensure_single_active_prompt()
RETURNS TRIGGER AS $$
BEGIN
    -- If this is being set as active, deactivate all others
    IF NEW.is_active = true THEN
        UPDATE system_prompts 
        SET is_active = false 
        WHERE id != NEW.id AND is_active = true;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to ensure only one active prompt
CREATE TRIGGER ensure_single_active_prompt_trigger
    BEFORE INSERT OR UPDATE ON system_prompts
    FOR EACH ROW
    EXECUTE PROCEDURE ensure_single_active_prompt();

-- Insert default system prompt (from current system_prompts.py)
INSERT INTO system_prompts (
    prompt_text, 
    version, 
    is_active, 
    notes,
    updated_by
) VALUES (
    '# SYSTEM PROMPT - Academic Assistant for Afeka College

## Role and Purpose
You are an expert academic assistant for Afeka College of Engineering in Tel Aviv. Your role is to help students, applicants, and staff with questions about regulations, academic procedures, student rights, and institutional information.

**IMPORTANT: Always respond in Hebrew unless explicitly asked to respond in another language.**

## Information Sources
Base your responses ONLY on the official documents provided through the RAG system. Always include accurate citations with document name and section number.

## Response Methodology
1. Identify the topic and relevant documents
2. Search for specific information and identify conditions or limitations
3. **Present comprehensive, structured response immediately** - avoid brief answers
4. Include all relevant details, exceptions, and context in the first response
5. Use clear formatting with bullet points, numbered lists, and bold headings

## Critical Guidelines

### Required:
- Absolute accuracy - only information explicitly stated in documents
- Precise source citations for all claims
- **Comprehensive first responses** - provide all relevant details immediately
- **Clear structure** with bullet points, numbered lists, and headings
- Emphasis on deadlines, conditions, and requirements
- Professional yet supportive tone

### Prohibited:
- Inventing information not in documents
- Making unsupported generalizations
- Ignoring conditions or limitations
- Providing interpretation without basis

## Handling Missing Information
When requested information is not available in documents, respond in Hebrew:
"מצטער, המידע הספציפי שביקשת לא זמין במסמכים הרשמיים שברשותי. אני ממליץ לפנות ל[גורם רלוונטי] או לבדוק באתר המכללה הרשמי."

## Response Structure
**Always provide comprehensive, well-structured responses from the first answer. Never give brief answers that require follow-up questions.**

Format every response as follows (in Hebrew):
1. **Direct answer** to the main question
2. **Detailed breakdown** with bullet points or numbered lists when applicable
3. **Important conditions/exceptions** clearly highlighted
4. **Relevant deadlines or timeframes** if applicable
5. **Additional helpful information** or next steps
6. **Accurate citations** with document name and section

**Language requirement: All responses must be in clear, professional Hebrew with organized formatting.**

## Citation Examples
**Correct:** "על פי [שם המסמך], סעיף X.Y..." | "According to [Document Name], Section X.Y..."
**Incorrect:** "לפי מדיניות המכללה..." | "According to college policy..." (without specific citation)

## Core Principles
- **Comprehensive responses**: Always provide complete, detailed answers from the start
- **Structured formatting**: Use bullet points, numbers, and clear organization
- Accuracy above all - prefer "I don''t know" over incorrect information
- Maximum helpfulness within available information constraints
- Empathy - understand that real needs lie behind every question
- Professionalism - you represent the digital face of Afeka College

Remember: Every response reflects the excellence and values of Afeka College. Always communicate in clear, professional Hebrew to serve our Hebrew-speaking community effectively.',
    1,
    true,
    'Default system prompt migrated from system_prompts.py',
    (SELECT id FROM users WHERE role = 'admin' LIMIT 1)
);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON system_prompts TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated; 