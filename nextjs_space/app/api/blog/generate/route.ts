

import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import { prisma } from '@/lib/db';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { contentType, title, subject, wordCount, keyword, keywords, seoTitle, metaDescription, youtubeUrl, listItems, wordsPerItem, tone } = body;

    // Support both 'title' and 'subject' for backwards compatibility
    const articleSubject = title || subject;
    // Support both 'keyword' (string) and 'keywords' (array)
    const articleKeywords = keywords || (keyword ? [keyword] : []);

    if (!contentType || !articleSubject) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields: contentType and title' },
        { status: 400 }
      );
    }

    // Ensure minimum word count for quality content
    const targetWordCount = Math.max(parseInt(wordCount) || 1500, 1000);

    let prompt = '';
    let systemPrompt = 'Je bent een professionele Nederlandse contentschrijver. Genereer hoogwaardige, uitgebreide en boeiende content in correct HTML-formaat. Schrijf altijd in het Nederlands. Zorg voor diepgaande informatie en uitgebreide uitleg.';

    switch (contentType) {
      case 'seo':
        const mainKeyword = articleKeywords.length > 0 ? articleKeywords[0] : articleSubject;
        const keywordDensity = Math.floor(targetWordCount / 150);
        prompt = `Schrijf een uitgebreid en diepgaand SEO-geoptimaliseerd artikel over "${articleSubject}" in het Nederlands.

Doelkeyword: ${mainKeyword}
${articleKeywords.length > 1 ? `Extra keywords: ${articleKeywords.slice(1).join(', ')}` : ''}
BELANGRIJK: Minimaal ${targetWordCount} woorden (streef naar ${targetWordCount + 500} woorden voor diepgaande content)
${seoTitle ? `SEO Titel: ${seoTitle}` : ''}
${metaDescription ? `Meta Beschrijving: ${metaDescription}` : ''}
Tone: ${tone || 'professioneel'}

Vereisten:
- Het artikel MOET minimaal ${targetWordCount} woorden bevatten
- Gebruik het hoofdkeyword natuurlijk ongeveer ${keywordDensity} keer in het artikel
- Gebruik HTML heading tags (h1 voor hoofdtitel, h2 voor secties, h3 voor subsecties)
- Gebruik paragrafen (<p>) en lijsten (<ul>, <ol>) waar passend
- Voeg een uitgebreide inleiding van minstens 150 woorden toe
- Maak minimaal 5-7 hoofdsecties met elk 200-400 woorden
- Voeg een uitgebreide conclusie van minstens 150 woorden toe
- Maak het informatief, gedetailleerd en SEO-vriendelijk
- Gebruik voorbeelden, statistieken en concrete informatie
- Schrijf volledig in het Nederlands

BELANGRIJK: Geef alleen de volledige HTML-content terug zonder markdown opmaak. Het artikel moet compleet en uitgebreid zijn.`;
        break;

      case 'listicle':
      case 'list':
        const listCount = listItems || 10;
        const wordsPerListItem = wordsPerItem || 150;
        const totalListWords = listCount * wordsPerListItem;
        prompt = `Schrijf een uitgebreid lijstje artikel in het Nederlands: "${articleSubject}"

Vereisten:
- Maak ${listCount} items
- Elk item MOET minimaal ${wordsPerListItem} woorden bevatten
- Totaal minimaal ${totalListWords + 300} woorden
- Gebruik HTML: <h1> voor hoofdtitel, <h2> voor elk lijstitem
- Nummer elk item duidelijk (1., 2., 3., etc.)
- Gebruik <p> tags voor paragrafen binnen elk item
- Maak elk item gedetailleerd, informatief en boeiend
- Voeg een uitgebreide inleiding van 150-200 woorden toe
- Voeg een uitgebreide conclusie van 150-200 woorden toe
- Geef concrete voorbeelden en details bij elk item
Tone: ${tone || 'professioneel'}

BELANGRIJK: Geef alleen de volledige HTML-content terug zonder markdown opmaak. Elk item moet uitgebreid en compleet zijn.`;
        break;

      case 'howto':
        prompt = `Schrijf een uitgebreide en gedetailleerde "How-to" gids in het Nederlands over "${articleSubject}".

${articleKeywords.length > 0 ? `Keywords: ${articleKeywords.join(', ')}` : ''}
BELANGRIJK: Minimaal ${targetWordCount} woorden (streef naar ${targetWordCount + 500} woorden)
Tone: ${tone || 'professioneel'}

Vereisten:
- Het artikel MOET minimaal ${targetWordCount} woorden bevatten
- Uitgebreide stap-voor-stap instructies
- Gebruik HTML heading tags (h1, h2, h3)
- Gebruik paragrafen (<p>) en genummerde lijsten (<ol>)
- Voeg een uitgebreide inleiding toe die het onderwerp verklaart
- Maak elke stap gedetailleerd (100-200 woorden per stap)
- Voeg tips, waarschuwingen en extra informatie toe
- Geef concrete voorbeelden en praktische adviezen
- Voeg een uitgebreide conclusie toe
- Volledig in het Nederlands

BELANGRIJK: Geef alleen de volledige HTML-content terug zonder markdown opmaak.`;
        break;

      case 'review':
        prompt = `Schrijf een uitgebreide en eerlijke review in het Nederlands over "${articleSubject}".

${articleKeywords.length > 0 ? `Keywords: ${articleKeywords.join(', ')}` : ''}
BELANGRIJK: Minimaal ${targetWordCount} woorden
Tone: ${tone || 'professioneel'}

Vereisten:
- Het artikel MOET minimaal ${targetWordCount} woorden bevatten
- Bespreek uitgebreid voor- en nadelen
- Gebruik HTML heading tags voor structuur
- Gebruik lijsten voor features en specificaties
- Geef een gedetailleerde analyse van elk aspect
- Vergelijk met alternatieven waar relevant
- Geef een eerlijke conclusie en aanbeveling
- Maak het informatief en gebalanceerd
- Volledig in het Nederlands

BELANGRIJK: Geef alleen de volledige HTML-content terug zonder markdown opmaak.`;
        break;

      case 'perplexity':
        prompt = `Schrijf een uitgebreid en diepgaand onderzoeksartikel in het Nederlands over "${articleSubject}".

${articleKeywords.length > 0 ? `Keywords: ${articleKeywords.join(', ')}` : ''}
BELANGRIJK: Minimaal ${targetWordCount} woorden (streef naar ${targetWordCount + 500} woorden)
Tone: ${tone || 'professioneel'}

Vereisten:
- Het artikel MOET minimaal ${targetWordCount} woorden bevatten
- Gebruik HTML heading tags (h1, h2, h3)
- Geef diepgaande analyse en onderzoek
- Gebruik concrete data, statistieken en bronnen
- Bespreek verschillende perspectieven
- Maak het uitgebreid, gedetailleerd en informatief
- Volledig in het Nederlands

BELANGRIJK: Geef alleen de volledige HTML-content terug zonder markdown opmaak.`;
        break;

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid content type' },
          { status: 400 }
        );
    }

    // Use gpt-4-turbo with increased token limit for longer content
    const completion = await openai.chat.completions.create({
      model: 'gpt-4-turbo-preview',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: prompt }
      ],
      temperature: 0.7,
      max_tokens: Math.min(8000, Math.ceil(targetWordCount * 2.5)) // Increased significantly for longer content
    });

    const content = completion.choices[0].message.content || '';

    // Calculate word count
    const plainText = content.replace(/<[^>]*>/g, '');
    const calculatedWordCount = plainText.split(/\s+/).filter(word => word.length > 0).length;

    // Log word count for debugging
    console.log(`Target word count: ${targetWordCount}, Generated: ${calculatedWordCount} words`);

    // Generate ID
    const { randomUUID } = await import('crypto');
    const postId = randomUUID();

    // Save to database
    const post = await prisma.blog_posts.create({
      data: {
        id: postId,
        title: articleSubject,
        content: content,
        htmlContent: content,
        contentType: contentType,
        keywords: articleKeywords.join(', '),
        seoTitle: seoTitle || articleSubject,
        metaDescription: metaDescription || '',
        status: 'draft',
        wordCount: calculatedWordCount,
        updatedAt: new Date(),
      },
    });

    return NextResponse.json({
      success: true,
      content: content,
      wordCount: calculatedWordCount,
      title: articleSubject,
      post
    });

  } catch (error: any) {
    console.error('Error generating blog content:', error);
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}

