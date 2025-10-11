
import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { prisma } from '@/lib/db';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { postType, platform, topic, tone, artStyle } = body;

    // Get art style description for prompt guidance
    const artStyleGuidance: { [key: string]: string } = {
      'comic': 'comic book style met bold kleuren en dynamische lijnen',
      'creepy-comic': 'horror comic style met donkere sfeer en dramatische schaduwen',
      'painting': 'klassieke schilderij style met rijke texturen',
      'ghibli': 'Studio Ghibli anime style met dromerige aesthetiek',
      'anime': 'moderne anime style met levendige kleuren',
      'dark-fantasy': 'dark fantasy style met mystieke elementen',
      'lego': 'LEGO blokjes style met plastic speelgoed uiterlijk',
      'polaroid': 'vintage polaroid foto style met retro uitstraling',
      'disney': 'Disney animatie style met magische visuals',
      'realism': 'fotorealistische style met hoge details',
      'fantastic': 'surrealistische fantasy art met droomachtige elementen',
    };

    const selectedStyleGuidance = artStyleGuidance[artStyle || 'realism'] || 'moderne artistieke style';

    // Generate content with OpenAI
    const contentPrompt = `Maak een korte, pakkende social media post voor ${platform} over het onderwerp: ${topic}.

Type: ${postType}
Tone: ${tone || 'inspirerend en positief'}
Gekozen visuele stijl: ${selectedStyleGuidance}

Geef de post in het volgende JSON formaat:
{
  "title": "Korte catchy titel (max 10 woorden)",
  "content": "De volledige post tekst (max 280 karakters voor Twitter, max 2200 voor andere platforms)",
  "hashtags": ["relevante", "hashtags", "5-10 stuks"],
  "imagePrompt": "Een ZEER SPECIFIEKE en GEDETAILLEERDE beschrijving voor DALL-E 3 om een pakkende afbeelding te genereren die DIRECT gerelateerd is aan het onderwerp. Beschrijf wat er letterlijk IN de afbeelding moet staan."
}

KRITIEKE REGELS voor imagePrompt:
1. Wees SPECIFIEK over het onderwerp - beschrijf wat er LETTERLIJK in de afbeelding moet staan
2. Noem SPECIFIEKE objecten, elementen, of concepten die passen bij het onderwerp
3. Beschrijf KLEUREN, BELICHTING en COMPOSITIE
4. Zorg dat de beschrijving relevant is voor het ONDERWERP
5. VERMIJD: generieke termen, mensen, gezichten
6. GEBRUIK: concrete objecten, symbolen, landschappen, voorwerpen, natuurelementen

Voorbeelden van GOEDE imagePrompts:
- Voor "Fitness": "Een heldere compositie van gekleurde halters, een yoga mat en verse groene smoothie op een houten tafel met natuurlijk licht"
- Voor "Motivatie": "Een winding bergpad die naar een stralende zonsopgang leidt, met mist in de valleien en gouden licht op de bergtoppen"
- Voor "Technologie": "Een futuristische workspace met holografische schermen, neon blauwe en paarse verlichting, en moderne tech gadgets"
- Voor "Natuur": "Een mysterieus oud bos met zonnestralen door de boomtoppen, groene bladeren en een pad bedekt met mos"

Maak de content engaging, relevant en optimaal voor ${platform}.`;

    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'Je bent een expert social media content creator die boeiende posts maakt voor verschillende platforms.',
        },
        {
          role: 'user',
          content: contentPrompt,
        },
      ],
      temperature: 0.8,
    });

    const generatedContent = JSON.parse(
      completion.choices[0].message.content || '{}'
    );

    // Generate image with DALL-E
    let imagePath = null;
    if (generatedContent.imagePrompt) {
      try {
        // Map art style to DALL-E style descriptors
        const artStyleDescriptions: { [key: string]: string } = {
          'comic': 'in vibrant comic book art style with bold outlines, dynamic composition, and vivid pop art colors',
          'creepy-comic': 'in dark horror comic art style with dramatic shadows, eerie atmosphere, and gothic elements',
          'painting': 'as a classical oil painting with rich textures, artistic brushstrokes, and fine art aesthetics',
          'ghibli': 'in Studio Ghibli animation style with whimsical, dreamy, and hand-painted watercolor aesthetics',
          'anime': 'in modern anime illustration style with expressive details, bold colors, and dynamic composition',
          'dark-fantasy': 'in dark fantasy art style with mystical atmosphere, dramatic lighting, and epic composition',
          'lego': 'made entirely of LEGO bricks and blocks with plastic toy-like appearance and bright colors',
          'polaroid': 'as a vintage polaroid photograph with retro 70s aesthetics, soft focus, and nostalgic colors',
          'disney': 'in Disney animation style with magical, enchanting visuals and storybook quality',
          'realism': 'as a photorealistic image with professional photography, high detail, and natural lighting',
          'fantastic': 'in surreal fantasy art style with dreamlike elements, imaginative visuals, and otherworldly atmosphere',
        };

        const styleDescription = artStyleDescriptions[artStyle || 'realism'] || 'in modern artistic style';

        // Create enhanced DALL-E prompt
        const enhancedImagePrompt = `${generatedContent.imagePrompt} ${styleDescription}. High quality social media graphic, professional composition, eye-catching and visually appealing. NO people, NO faces, NO human figures in the image.`;

        console.log('DALL-E Prompt:', enhancedImagePrompt);

        const imageResponse = await openai.images.generate({
          model: 'dall-e-3',
          prompt: enhancedImagePrompt,
          n: 1,
          size: '1024x1024',
          quality: 'hd',
        });

        imagePath = imageResponse.data?.[0]?.url || null;
        console.log('Generated image URL:', imagePath);
      } catch (imageError: any) {
        console.error('Error generating image:', imageError);
        console.error('Error details:', imageError.message);
        // Continue without image if generation fails
      }
    }

    // Save to database
    const post = await prisma.social_media_posts.create({
      data: {
        title: generatedContent.title,
        content: generatedContent.content,
        platform: platform || 'all',
        postType: postType || 'motivational',
        imagePrompt: generatedContent.imagePrompt,
        imagePath: imagePath,
        hashtags: generatedContent.hashtags || [],
        status: 'draft',
        artStyle: artStyle || 'realism',
      },
    });

    return NextResponse.json({
      success: true,
      post,
      generated: generatedContent,
    });
  } catch (error: any) {
    console.error('Error generating social media post:', error);
    return NextResponse.json(
      { success: false, error: error.message || 'Failed to generate post' },
      { status: 500 }
    );
  }
}
