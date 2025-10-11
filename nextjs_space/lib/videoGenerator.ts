
import fs from 'fs';
import path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execPromise = promisify(exec);

interface VideoGenerationConfig {
  format: string;
  presetType?: string;
  customFormat?: string;
  niche: string;
  language: string;
  voice: string;
  voiceStyle: string;
  backgroundMusic?: string;
  artStyle: string;
  captionStyle: string;
  duration: string;
}

interface Scene {
  text: string;
  visualPrompt: string;
  duration: number;
}

// Load API keys
function getApiKeys() {
  try {
    // Try multiple paths for auth secrets file (dynamically constructed to avoid Next.js build errors)
    const homeDir = process.env.HOME || '';
    const possiblePaths = [
      homeDir ? `${homeDir}${String.fromCharCode(47)}.config${String.fromCharCode(47)}abacusai_auth_secrets.json` : null,
    ].filter(Boolean) as string[];
    
    for (const secretsPath of possiblePaths) {
      if (fs.existsSync(secretsPath)) {
        try {
          const secrets = JSON.parse(fs.readFileSync(secretsPath, 'utf-8'));
          const openaiKey = secrets.openai?.secrets?.api_key?.value;
          const elevenlabsKey = secrets.elevenlabs?.secrets?.api_key?.value;
          
          if (openaiKey || elevenlabsKey) {
            console.log('✅ Loaded API keys from auth secrets');
            return {
              openai: openaiKey || process.env.OPENAI_API_KEY,
              elevenlabs: elevenlabsKey || process.env.ELEVENLABS_API_KEY,
            };
          }
        } catch (parseError) {
          console.error('Error parsing auth secrets:', parseError);
        }
      }
    }
  } catch (error) {
    console.error('Error loading API keys from auth secrets:', error);
  }
  
  // Fallback to environment variables
  console.log('⚠️  Using API keys from environment variables');
  return {
    openai: process.env.OPENAI_API_KEY,
    elevenlabs: process.env.ELEVENLABS_API_KEY,
  };
}

// Get style guide based on niche/topic
function getNicheStyleGuide(niche: string, voiceStyle: string): string {
  const nicheLower = niche.toLowerCase();
  
  // Dark/Mysterious content (crime, horror, mysteries)
  if (nicheLower.includes('crime') || nicheLower.includes('mystery') || nicheLower.includes('horror') || 
      nicheLower.includes('dark') || nicheLower.includes('scary') || nicheLower.includes('creepy')) {
    return `STYLE FOR THIS NICHE:
→ Start with something SHOCKING or mysterious
→ Build suspense and tension throughout
→ Use dramatic reveals: "But then..." "What they found next..."
→ Dark, moody tone but still conversational
→ Example hooks: "Nobody expected what they'd find..." / "This is the story of..."`;
  }
  
  // Motivational/Inspirational content
  if (nicheLower.includes('motivat') || nicheLower.includes('inspir') || nicheLower.includes('success') ||
      nicheLower.includes('mindset') || nicheLower.includes('entrepreneur')) {
    return `STYLE FOR THIS NICHE:
→ Start with a powerful statement or question
→ Tell transformation stories (from struggle to success)
→ Use relatable language: "We all face..." "You know that feeling..."
→ Uplifting but real tone (not cheesy)
→ Example hooks: "Want to know the real secret?" / "This changed everything for me..."`;
  }
  
  // Educational/Fact-based content
  if (nicheLower.includes('history') || nicheLower.includes('science') || nicheLower.includes('fact') ||
      nicheLower.includes('educat') || nicheLower.includes('learn')) {
    return `STYLE FOR THIS NICHE:
→ Start with a surprising fact or question
→ Make complex topics simple and interesting
→ Use comparisons people understand: "Imagine if..." "That's like..."
→ Informative but entertaining tone
→ Example hooks: "Did you know that..." / "Here's something wild..."`;
  }
  
  // Lifestyle/Entertainment content
  if (nicheLower.includes('lifestyle') || nicheLower.includes('travel') || nicheLower.includes('food') ||
      nicheLower.includes('fashion') || nicheLower.includes('entertainment')) {
    return `STYLE FOR THIS NICHE:
→ Start with something visually or emotionally appealing
→ Make it feel personal and relatable
→ Use vivid descriptions that paint pictures
→ Fun, engaging tone
→ Example hooks: "You have to see this..." / "This is incredible..."`;
  }
  
  // Business/Finance content
  if (nicheLower.includes('business') || nicheLower.includes('money') || nicheLower.includes('finance') ||
      nicheLower.includes('invest') || nicheLower.includes('marketing')) {
    return `STYLE FOR THIS NICHE:
→ Start with a valuable insight or surprising stat
→ Give actionable information
→ Use real examples and case studies
→ Professional but conversational tone
→ Example hooks: "This one trick changed the game..." / "Most people don't know this..."`;
  }
  
  // Default: Universal engaging style
  return `STYLE FOR THIS NICHE:
→ Start with your strongest, most interesting point
→ Tell it like a story with a clear beginning, middle, and end
→ Use specific examples and details
→ Conversational, engaging tone - like telling a friend
→ Example hooks: "Let me tell you about..." / "This is wild..."`;
}

// Generate script using OpenAI
export async function generateScript(config: VideoGenerationConfig, videoIndex: number): Promise<string> {
  const apiKeys = getApiKeys();
  
  if (!apiKeys.openai) {
    throw new Error('OpenAI API key not found. Please configure it in the auth secrets or environment variables.');
  }
  
  console.log('🔑 OpenAI API key found:', apiKeys.openai.substring(0, 10) + '...');
  
  const formatDescription = config.format === 'preset' 
    ? getPresetDescription(config.presetType || '')
    : getCustomFormatDescription(config.customFormat || '');
  
  const targetDuration = config.duration === 'short' ? '30-60 seconds' : '3-5 minutes';
  
  // Determine the style approach based on niche
  const nicheStyleGuide = getNicheStyleGuide(config.niche, config.voiceStyle);
  
  const prompt = `Create a ${formatDescription} video script about "${config.niche}".

CRITICAL: Write like a HUMAN talking naturally, not like AI or a textbook.

${nicheStyleGuide}

UNIVERSAL RULES (for ALL niches):
✓ HOOK: First 3 seconds MUST grab attention immediately
✓ NATURAL SPEECH: Write like you're talking to a friend over coffee
✓ SHORT SENTENCES: Keep it punchy. Easy to follow. Like this.
✓ SPECIFIC DETAILS: Use real names, numbers, places, dates (makes it believable)
✓ EMOTION: Make viewers FEEL something (curiosity, surprise, inspiration, shock)
✓ PACING: Build momentum. Keep them watching until the end.
✓ NO FLUFF: Every sentence must add value. No boring intros.

FORMAT:
- Duration: ${targetDuration}
- Language: ${config.language}
- Voice tone: ${config.voiceStyle}
- Video ${videoIndex + 1} in series (make it UNIQUE and FRESH)
- Word count: ${config.duration === 'short' ? '80-150' : '400-700'} words

WRITE ONLY THE NARRATION - no [brackets], no stage directions, no scene numbers.

Start writing NOW:`;

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${apiKeys.openai}`,
    },
    body: JSON.stringify({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: 'You are a viral storyteller who creates addictive, binge-worthy content. Your scripts make people stop scrolling and watch until the end. You tell true stories in a dramatic, conversational way that sounds natural and engaging - like a friend sharing something shocking over coffee. No corporate speak, no textbook language. Just raw, compelling storytelling.' },
        { role: 'user', content: prompt }
      ],
      temperature: 0.9,
      max_tokens: config.duration === 'short' ? 300 : 1000,
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('❌ OpenAI API error:', {
      status: response.status,
      statusText: response.statusText,
      body: errorBody,
    });
    throw new Error(`OpenAI API error: ${response.status} ${response.statusText} - ${errorBody}`);
  }

  const data = await response.json();
  return data.choices[0].message.content.trim();
}

// Split script into scenes
export function splitIntoScenes(script: string, duration: string, artStyle: string): Scene[] {
  const sentences = script.match(/[^.!?]+[.!?]+/g) || [script];
  
  // For short videos (30-60s): 5-7 scenes of 8 seconds each = 40-56 seconds
  // For long videos (3-5min): 15-20 scenes of 10 seconds each = 150-200 seconds (2.5-3.3 min)
  const sceneCount = duration === 'short' ? 6 : 18;
  const sceneDuration = duration === 'short' ? 8 : 10;
  
  const scenesPerGroup = Math.ceil(sentences.length / sceneCount);
  const scenes: Scene[] = [];
  
  for (let i = 0; i < sceneCount; i++) {
    const start = i * scenesPerGroup;
    const end = Math.min(start + scenesPerGroup, sentences.length);
    const sceneText = sentences.slice(start, end).join(' ').trim();
    
    if (sceneText) {
      scenes.push({
        text: sceneText,
        visualPrompt: generateVisualPrompt(sceneText, artStyle),
        duration: sceneDuration,
      });
    }
  }
  
  return scenes;
}

// Generate visual prompt for a scene
function generateVisualPrompt(text: string, artStyle: string): string {
  const styleDescriptions: Record<string, string> = {
    'realism': 'photorealistic, cinematic lighting, dramatic composition, high quality, 4K detail',
    'fantastic': 'fantasy art, epic scale, magical atmosphere, dramatic lighting, cinematic',
    'polaroid': 'vintage polaroid aesthetic, nostalgic, moody lighting, cinematic composition',
    'disney': '3D Disney Pixar style, expressive characters, dramatic lighting, emotional scene',
    'comic': 'comic book illustration, bold lines, dramatic colors, dynamic composition, cinematic angle',
    'creepy-comic': 'dark illustrated comic style, noir aesthetic, moody atmospheric lighting, dramatic shadows, cinematic framing, muted color palette with accent colors, mysterious and ominous mood',
    'painting': 'cinematic digital painting, dramatic lighting, rich colors, dynamic composition',
  };
  
  const style = styleDescriptions[artStyle] || 'cinematic, dramatic, professional';
  
  // Instead of using the script text directly (which may contain policy-violating content),
  // generate safe, abstract visual descriptions based on the art style
  // This ensures DALL-E compliance while maintaining visual variety
  
  const safeVisualConcepts = [
    'a dimly lit room with atmospheric fog and moody blue tones',
    'an empty hallway with dramatic shadows and warm lighting',
    'a mysterious forest path with fog and evening light',
    'an old building interior with vintage furniture and soft lighting',
    'a dramatic sky with storm clouds and cinematic composition',
    'an abandoned location with overgrown plants and ethereal lighting',
    'a quiet street at dusk with street lamps and atmospheric haze',
    'an antique room with vintage objects and dramatic side lighting',
    'a foggy landscape with silhouettes and moody atmosphere',
    'an old library with books and warm candlelight'
  ];
  
  // Select a visual concept based on text length (pseudo-random but consistent)
  const index = text.length % safeVisualConcepts.length;
  const sceneDescription = safeVisualConcepts[index];
  
  const prompt = `${sceneDescription}, ${style}, highly detailed, no text overlay, no watermarks, professional quality, cinematic composition, appropriate for all audiences, no people, no violence`;
  
  return prompt;
}

// Generate voiceover using ElevenLabs
export async function generateVoiceover(text: string, voice: string, outputPath: string): Promise<void> {
  const apiKeys = getApiKeys();
  
  // ElevenLabs voice IDs (mapping from our voice names)
  const voiceIds: Record<string, string> = {
    'Adam': '21m00Tcm4TlvDq8ikWAM',
    'John': 'pNInz6obpgDQGcFmaJgB',
  };
  
  const voiceId = voiceIds[voice] || voiceIds['Adam'];
  
  const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'xi-api-key': apiKeys.elevenlabs,
    },
    body: JSON.stringify({
      text,
      model_id: 'eleven_multilingual_v2',
      voice_settings: {
        stability: 0.5,
        similarity_boost: 0.75,
      },
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    console.error('❌ ElevenLabs API error:', {
      status: response.status,
      statusText: response.statusText,
      body: errorBody,
    });
    throw new Error(`ElevenLabs API error: ${response.status} ${response.statusText} - ${errorBody}`);
  }

  const audioBuffer = await response.arrayBuffer();
  fs.writeFileSync(outputPath, Buffer.from(audioBuffer));
}

// Helper functions
function getPresetDescription(presetType: string): string {
  const presets: Record<string, string> = {
    'scary-stories': 'scary story that gives goosebumps',
    'history': 'historical story from ancient or modern times',
    'true-crime': 'true crime story',
  };
  return presets[presetType] || 'engaging story';
}

function getCustomFormatDescription(customFormat: string): string {
  const formats: Record<string, string> = {
    'storytelling': 'engaging story with surprising twists',
    'what-if': 'fascinating hypothetical scenario',
    '5-things': 'mind-blowing facts and hidden secrets',
    'random-fact': 'interesting random fact',
  };
  return formats[customFormat] || 'engaging content';
}

// Assemble video with FFmpeg
export async function assembleVideo(
  videoClips: string[],
  audioPath: string,
  outputPath: string,
  backgroundMusic?: string,
): Promise<void> {
  // Create a concat file for FFmpeg
  const concatFilePath = path.join(path.dirname(outputPath), 'concat.txt');
  const concatContent = videoClips.map(clip => `file '${clip}'`).join('\n');
  fs.writeFileSync(concatFilePath, concatContent);
  
  try {
    console.log('Concatenating video clips...');
    // Concatenate video clips (re-encode to ensure compatibility)
    const tempVideoPath = path.join(path.dirname(outputPath), 'temp_video.mp4');
    await execPromise(
      `ffmpeg -y -f concat -safe 0 -i "${concatFilePath}" ` +
      `-c:v libx264 -preset veryfast -profile:v high -level 4.0 -pix_fmt yuv420p -r 24 -movflags +faststart "${tempVideoPath}"`,
      { timeout: 180000 } // 3 minute timeout
    );
    
    console.log('Adding audio...');
    // Add audio
    if (backgroundMusic && fs.existsSync(backgroundMusic)) {
      // Mix voiceover with background music
      await execPromise(
        `ffmpeg -y -i "${tempVideoPath}" -i "${audioPath}" -i "${backgroundMusic}" ` +
        `-filter_complex "[1:a]volume=1.0[a1];[2:a]volume=0.2[a2];[a1][a2]amix=inputs=2:duration=first[aout]" ` +
        `-map 0:v -map "[aout]" -c:v copy -c:a aac -b:a 128k -ar 44100 -movflags +faststart "${outputPath}"`,
        { timeout: 180000 } // 3 minute timeout
      );
    } else {
      // Just add voiceover
      await execPromise(
        `ffmpeg -y -i "${tempVideoPath}" -i "${audioPath}" ` +
        `-c:v copy -c:a aac -b:a 128k -ar 44100 -movflags +faststart "${outputPath}"`,
        { timeout: 180000 } // 3 minute timeout
      );
    }
    
    // Cleanup temp files
    if (fs.existsSync(tempVideoPath)) {
      fs.unlinkSync(tempVideoPath);
    }
    if (fs.existsSync(concatFilePath)) {
      fs.unlinkSync(concatFilePath);
    }
  } catch (error) {
    console.error('FFmpeg error:', error);
    throw error;
  }
}

// Generate AI image using DALL-E 3
async function generateAIImage(visualPrompt: string, imagePath: string, artStyle: string): Promise<boolean> {
  try {
    const apiKeys = getApiKeys();
    
    if (!apiKeys.openai) {
      console.log('No OpenAI API key found');
      return false;
    }
    
    // The visualPrompt already includes the style, just add format requirements
    const dallePrompt = `${visualPrompt}, vertical format, 9:16 aspect ratio, no text or watermarks, safe for work, appropriate for all audiences`;
    
    console.log('Generating AI image with DALL-E 3:', dallePrompt.substring(0, 100) + '...');
    
    // Call DALL-E 3 API
    const response = await fetch('https://api.openai.com/v1/images/generations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKeys.openai}`,
      },
      body: JSON.stringify({
        model: 'dall-e-3',
        prompt: dallePrompt,
        n: 1,
        size: '1024x1792', // Vertical format (9:16 ratio)
        quality: 'hd',
        style: artStyle === 'realism' ? 'natural' : 'vivid',
      }),
    });
    
    if (!response.ok) {
      const error = await response.json();
      console.error('DALL-E 3 API error:', error);
      return false;
    }
    
    const data = await response.json();
    const imageUrl = data.data[0].url;
    
    console.log('AI image generated, downloading...');
    
    // Download the generated image
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) {
      console.error('Failed to download generated image');
      return false;
    }
    
    const buffer = await imageResponse.arrayBuffer();
    fs.writeFileSync(imagePath, Buffer.from(buffer));
    
    console.log('AI image saved successfully:', imagePath);
    return true;
  } catch (error) {
    console.error('Error generating AI image:', error);
    return false;
  }
}

// Generate video clip for a scene (with motion effects on AI-generated image)
async function generateVideoClip(
  scene: Scene, 
  index: number, 
  outputDir: string, 
  artStyle: string,
  onProgress?: (message: string) => void
): Promise<string> {
  const outputPath = path.join(outputDir, `scene_${index}.mp4`);
  const imagePath = path.join(outputDir, `scene_${index}.jpg`);
  
  const duration = scene.duration;
  
  try {
    // Generate AI image using DALL-E 3
    if (onProgress) onProgress(`Genereren van AI-afbeelding voor scene ${index + 1}...`);
    
    const imageGenerated = await generateAIImage(scene.visualPrompt, imagePath, artStyle);
    
    if (!imageGenerated) {
      // Fallback: Try Pixabay stock images
      if (onProgress) onProgress(`Fallback naar stock afbeeldingen voor scene ${index + 1}...`);
      const imageDownloaded = await downloadSceneImage(scene.visualPrompt, imagePath, scene.visualPrompt);
      
      if (!imageDownloaded) {
        // Last fallback: create a gradient background
        if (onProgress) onProgress(`Maken van fallback achtergrond voor scene ${index + 1}...`);
        await createFallbackImage(imagePath, index);
      }
    }
    
    // Apply motion effects to the image using FFmpeg
    if (onProgress) onProgress(`Toepassen van bewegingseffecten op scene ${index + 1}...`);
    
    // Use simplified motion effects for faster processing
    const motionTypes = ['zoom-in', 'zoom-out', 'pan-right', 'pan-left', 'static'];
    const motionType = motionTypes[index % motionTypes.length];
    
    let filterCommand = '';
    const fps = 24;
    const frames = Math.ceil(duration * fps);
    
    switch (motionType) {
      case 'zoom-in':
        filterCommand = `zoompan=z='min(zoom+0.002,1.3)':d=${frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=${fps}`;
        break;
      case 'zoom-out':
        filterCommand = `zoompan=z='if(lte(zoom,1.0),1.3,max(1.0,zoom-0.002))':d=${frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=${fps}`;
        break;
      case 'pan-right':
        filterCommand = `zoompan=z=1.2:d=${frames}:x='if(gte(on,1),x+3,x)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=${fps}`;
        break;
      case 'pan-left':
        filterCommand = `zoompan=z=1.2:d=${frames}:x='if(gte(on,1),x-3,x)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=${fps}`;
        break;
      default:
        // Static with slight zoom
        filterCommand = `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=${fps}`;
    }
    
    console.log(`Applying ${motionType} effect to scene ${index + 1}...`);
    
    const ffmpegCommand = `ffmpeg -y -loop 1 -i "${imagePath}" -vf "${filterCommand}" -t ${duration} -c:v libx264 -preset veryfast -crf 23 -pix_fmt yuv420p "${outputPath}"`;
    
    console.log('FFmpeg command:', ffmpegCommand);
    
    try {
      const { stdout, stderr } = await execPromise(ffmpegCommand, { timeout: 60000 }); // 60 second timeout
      console.log('FFmpeg completed for scene', index + 1);
    } catch (error: any) {
      console.error('FFmpeg error details:', error);
      if (error.killed) {
        throw new Error(`FFmpeg timeout na 60 seconden voor scene ${index + 1}`);
      }
      throw error;
    }
    
    return outputPath;
  } catch (error) {
    console.error(`Error generating video clip ${index}:`, error);
    throw error;
  }
}

// Download image from Pixabay for a scene
async function downloadSceneImage(visualPrompt: string, outputPath: string, niche: string): Promise<boolean> {
  try {
    // Extract keywords from visual prompt
    const keywords = extractKeywords(visualPrompt, niche);
    
    // Try to read Pixabay API key from auth secrets
    let pixabayKey = process.env.PIXABAY_API_KEY;
    
    try {
      const secretsPath = process.env.HOME ? `${process.env.HOME}/.config/abacusai_auth_secrets.json` : null;
      if (secretsPath && fs.existsSync(secretsPath)) {
        const secrets = JSON.parse(fs.readFileSync(secretsPath, 'utf-8'));
        pixabayKey = secrets.pixabay?.secrets?.api_key?.value || pixabayKey;
      }
    } catch (e) {
      // Ignore errors, use env var
    }
    
    if (!pixabayKey) {
      console.log('No Pixabay API key found, using fallback images');
      return false;
    }
    
    // Search for images using Pixabay API
    const apiUrl = 'https://pixabay.com/api/';
    const params = new URLSearchParams({
      key: pixabayKey,
      q: keywords,
      image_type: 'photo',
      orientation: 'vertical',
      per_page: '10',
      safesearch: 'true'
    });
    
    const searchUrl = `${apiUrl}?${params.toString()}`;
    
    const response = await fetch(searchUrl);
    if (!response.ok) {
      console.log('Pixabay API error:', response.status, response.statusText);
      return false;
    }
    
    const data = await response.json();
    if (!data.hits || data.hits.length === 0) {
      console.log('No images found for keywords:', keywords);
      return false;
    }
    
    // Get a random image from results
    const randomIndex = Math.floor(Math.random() * Math.min(data.hits.length, 5));
    const imageUrl = data.hits[randomIndex].largeImageURL;
    
    console.log('Downloading image:', imageUrl);
    
    // Download the image
    const imageResponse = await fetch(imageUrl);
    if (!imageResponse.ok) {
      return false;
    }
    
    const buffer = await imageResponse.arrayBuffer();
    fs.writeFileSync(outputPath, Buffer.from(buffer));
    
    console.log('Image downloaded successfully to:', outputPath);
    return true;
  } catch (error) {
    console.error('Error downloading image from Pixabay:', error);
    return false;
  }
}

// Extract keywords from visual prompt
function extractKeywords(visualPrompt: string, niche: string): string {
  // Remove style descriptions and technical terms
  const cleaned = visualPrompt
    .toLowerCase()
    .replace(/photorealistic|high quality|detailed|cinematic|professional|no text|no watermarks/gi, '')
    .replace(/\.\.\./g, '')
    .trim();
  
  // Combine with niche for better results
  const keywords = `${niche} ${cleaned}`.substring(0, 100);
  
  return keywords;
}

// Create a fallback gradient image
async function createFallbackImage(outputPath: string, index: number): Promise<void> {
  const colors = [
    '#1a1a2e',  // Dark blue
    '#16213e',  // Navy
    '#0f3460',  // Deep blue
    '#2c3e50',  // Slate
    '#34495e',  // Dark gray-blue
    '#2c2c54',  // Purple navy
  ];
  
  const color = colors[index % colors.length];
  
  // Create a simple solid color image using FFmpeg
  await execPromise(
    `ffmpeg -y -f lavfi -i "color=c=${color}:s=1080x1920:d=1" ` +
    `-frames:v 1 "${outputPath}"`
  );
  
  console.log(`Created fallback image: ${outputPath}`);
}

// Main video generation function
export async function generateVideo(
  config: VideoGenerationConfig,
  videoIndex: number,
  outputDir: string,
  onProgress?: (step: string, percentage: number) => void,
): Promise<{ videoPath: string; title: string; duration: string }> {
  console.log(`Generating video ${videoIndex + 1}...`);
  
  try {
    // 1. Generate script
    console.log('Generating script...');
    if (onProgress) onProgress('Script wordt geschreven...', 10);
    const script = await generateScript(config, videoIndex);
    const title = script.split('.')[0].substring(0, 100);
    
    // 2. Split into scenes
    console.log('Splitting into scenes...');
    if (onProgress) onProgress('Scenes worden voorbereid...', 15);
    const scenes = splitIntoScenes(script, config.duration, config.artStyle);
    console.log(`Created ${scenes.length} scenes`);
    
    // 3. Generate video clips for each scene
    console.log('Generating video clips...');
    const videoClips: string[] = [];
    for (let i = 0; i < scenes.length; i++) {
      const sceneProgress = 15 + ((i / scenes.length) * 50);
      if (onProgress) onProgress(`Scene ${i + 1}/${scenes.length} wordt gegenereerd...`, sceneProgress);
      console.log(`Generating scene ${i + 1}/${scenes.length}...`);
      const clipPath = await generateVideoClip(
        scenes[i], 
        i, 
        outputDir, 
        config.artStyle,
        (msg) => {
          console.log(msg);
          if (onProgress) onProgress(msg, sceneProgress);
        }
      );
      videoClips.push(clipPath);
    }
    
    // 4. Generate voiceover
    console.log('Generating voiceover...');
    if (onProgress) onProgress('Voice-over wordt gegenereerd...', 70);
    const audioPath = path.join(outputDir, `audio_${videoIndex}.mp3`);
    await generateVoiceover(script, config.voice, audioPath);
    
    // 5. Assemble final video
    console.log('Assembling final video...');
    if (onProgress) onProgress('Video wordt samengesteld...', 85);
    const videoPath = path.join(outputDir, `video_${videoIndex}.mp4`);
    const backgroundMusic = config.backgroundMusic 
      ? path.join(process.cwd(), 'public', 'music', `${config.backgroundMusic}.mp3`)
      : undefined;
    
    await assembleVideo(videoClips, audioPath, videoPath, backgroundMusic);
    
    // 6. Generate thumbnail
    console.log('Generating thumbnail...');
    if (onProgress) onProgress('Thumbnail wordt gemaakt...', 95);
    const thumbnailPath = path.join(outputDir, `thumbnail_${videoIndex}.jpg`);
    await execPromise(
      `ffmpeg -y -i "${videoPath}" -ss 00:00:01 -vframes 1 "${thumbnailPath}"`,
      { timeout: 30000 } // 30 second timeout
    );
    
    // 7. Cleanup temp files
    console.log('Cleaning up...');
    if (onProgress) onProgress('Bestanden worden opgeschoond...', 98);
    for (const clipPath of videoClips) {
      if (fs.existsSync(clipPath)) {
        fs.unlinkSync(clipPath);
      }
    }
    // Also cleanup scene images
    for (let i = 0; i < scenes.length; i++) {
      const imagePath = path.join(outputDir, `scene_${i}.jpg`);
      if (fs.existsSync(imagePath)) {
        fs.unlinkSync(imagePath);
      }
    }
    if (fs.existsSync(audioPath)) {
      fs.unlinkSync(audioPath);
    }
    
    // Calculate actual duration
    const { stdout } = await execPromise(
      `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${videoPath}"`
    );
    const durationSeconds = Math.round(parseFloat(stdout.trim()));
    const durationStr = durationSeconds >= 60 
      ? `${Math.floor(durationSeconds / 60)}m ${durationSeconds % 60}s`
      : `${durationSeconds}s`;
    
    console.log(`Video ${videoIndex + 1} generated successfully!`);
    if (onProgress) onProgress('Video voltooid!', 100);
    
    return {
      videoPath,
      title,
      duration: durationStr,
    };
  } catch (error) {
    console.error(`Error generating video ${videoIndex + 1}:`, error);
    throw error;
  }
}
