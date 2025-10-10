// Website Management Modal with Tabs
// Comprehensive website settings interface

let currentTab = 'basic';

async function openWebsiteManagementModal(websiteId) {
    try {
        // Fetch comprehensive website data
        const response = await fetch(`/api/websites/${websiteId}/management`);
        const data = await response.json();
        
        if (!data.success) {
            showNotification('Fout bij laden website gegevens', 'error');
            return;
        }
        
        const website = data.website;
        
        // Create modal with tabs
        const modal = document.createElement('div');
        modal.id = 'website-management-modal';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); z-index: 10000; display: flex; align-items: center; justify-content: center; padding: 20px;';
        modal.onclick = closeWebsiteManagementModal;
        
        modal.innerHTML = `
            <div style="background: white; border-radius: 16px; max-width: 900px; width: 100%; max-height: 85vh; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.3);" onclick="event.stopPropagation()">
                <!-- Header -->
                <div style="padding: 24px; border-bottom: 2px solid #e0e0e0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h3 style="margin: 0 0 5px 0; color: white; font-size: 22px;">🌐 Website Beheer</h3>
                            <p style="margin: 0; font-size: 14px; color: rgba(255,255,255,0.9);">${website.name}</p>
                        </div>
                        <button onclick="closeWebsiteManagementModal()" style="background: rgba(255,255,255,0.2); border: none; font-size: 24px; cursor: pointer; color: white; padding: 0; width: 36px; height: 36px; border-radius: 50%; transition: all 0.3s;" onmouseover="this.style.background='rgba(255,255,255,0.3)'" onmouseout="this.style.background='rgba(255,255,255,0.2)'">&times;</button>
                    </div>
                </div>
                
                <!-- Tabs -->
                <div style="display: flex; border-bottom: 1px solid #e0e0e0; background: #f8f9fa; overflow-x: auto;">
                    <button onclick="switchTab('basic', ${websiteId})" id="tab-basic" class="mgmt-tab active" style="flex: 1; min-width: 120px; padding: 16px 20px; border: none; background: none; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s;">
                        📋 Basis Info
                    </button>
                    <button onclick="switchTab('context', ${websiteId})" id="tab-context" class="mgmt-tab" style="flex: 1; min-width: 120px; padding: 16px 20px; border: none; background: none; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s;">
                        💡 Context
                    </button>
                    <button onclick="switchTab('links', ${websiteId})" id="tab-links" class="mgmt-tab" style="flex: 1; min-width: 120px; padding: 16px 20px; border: none; background: none; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s;">
                        🔗 Externe Links
                    </button>
                    <button onclick="switchTab('schedule', ${websiteId})" id="tab-schedule" class="mgmt-tab" style="flex: 1; min-width: 120px; padding: 16px 20px; border: none; background: none; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s;">
                        📅 Planning
                    </button>
                    <button onclick="switchTab('wordpress', ${websiteId})" id="tab-wordpress" class="mgmt-tab" style="flex: 1; min-width: 120px; padding: 16px 20px; border: none; background: none; cursor: pointer; font-size: 14px; font-weight: 600; color: #666; border-bottom: 3px solid transparent; transition: all 0.3s;">
                        🔌 WordPress
                    </button>
                </div>
                
                <!-- Content -->
                <form id="website-management-form" onsubmit="saveWebsiteManagement(event, ${websiteId})" style="max-height: calc(85vh - 200px); overflow-y: auto;">
                    <div style="padding: 24px;">
                        ${renderTabContent('basic', website, websiteId)}
                    </div>
                </form>
                
                <!-- Footer -->
                <div style="padding: 20px 24px; border-top: 1px solid #e0e0e0; background: #f8f9fa; display: flex; gap: 12px; justify-content: flex-end;">
                    <button type="button" onclick="closeWebsiteManagementModal()" class="btn btn-secondary" style="padding: 12px 24px;">
                        Annuleren
                    </button>
                    <button type="button" onclick="document.getElementById('website-management-form').requestSubmit()" class="btn btn-primary" style="padding: 12px 24px;">
                        💾 Opslaan
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add active tab style
        updateActiveTab('basic');
        
    } catch (error) {
        console.error('Error opening website management modal:', error);
        showNotification('Fout bij laden: ' + error.message, 'error');
    }
}

function renderTabContent(tab, website, websiteId) {
    switch(tab) {
        case 'basic':
            return `
                <div id="tab-content-basic" class="tab-content">
                    <h4 style="margin: 0 0 20px 0; color: var(--dark-blue); font-size: 18px;">Basis Informatie</h4>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Website Naam *</label>
                        <input type="text" id="website-name" value="${website.name || ''}" required style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">URL</label>
                        <input type="url" id="website-url" value="${website.url || ''}" readonly style="width: 100%; padding: 12px; border: 1px solid #e0e0e0; border-radius: 8px; font-size: 14px; background: #f8f9fa; color: #666;">
                        <small style="color: #666; font-size: 12px;">URL kan niet worden gewijzigd</small>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Niche / Industrie</label>
                        <input type="text" id="website-niche" value="${website.niche || ''}" placeholder="bijv. Digital Marketing, E-commerce, Gezondheid" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                        <small style="color: #666; font-size: 12px;">De industrie of niche waarin je website actief is</small>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Doelgroep</label>
                        <input type="text" id="website-audience" value="${website.target_audience || ''}" placeholder="bijv. Ondernemers, Consumenten, B2B beslissers" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                        <small style="color: #666; font-size: 12px;">Wie zijn je ideale bezoekers/klanten?</small>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Tone of Voice</label>
                        <select id="website-tone" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                            <option value="professional" ${(website.tone_of_voice || 'professional') === 'professional' ? 'selected' : ''}>Professioneel</option>
                            <option value="casual" ${website.tone_of_voice === 'casual' ? 'selected' : ''}>Casual</option>
                            <option value="friendly" ${website.tone_of_voice === 'friendly' ? 'selected' : ''}>Vriendelijk</option>
                            <option value="formal" ${website.tone_of_voice === 'formal' ? 'selected' : ''}>Formeel</option>
                            <option value="inspirational" ${website.tone_of_voice === 'inspirational' ? 'selected' : ''}>Inspirerend</option>
                            <option value="educational" ${website.tone_of_voice === 'educational' ? 'selected' : ''}>Educatief</option>
                        </select>
                        <small style="color: #666; font-size: 12px;">De schrijfstijl voor je content</small>
                    </div>
                </div>
            `;
            
        case 'context':
            return `
                <div id="tab-content-context" class="tab-content">
                    <h4 style="margin: 0 0 20px 0; color: var(--dark-blue); font-size: 18px;">Context & Knowledgebase</h4>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Website Context</label>
                        <textarea id="website-context" rows="6" placeholder="Beschrijf je website, bedrijf, producten, diensten, USPs, etc..." style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: inherit; resize: vertical;">${website.context || ''}</textarea>
                        <small style="color: #666; font-size: 12px;">Deze informatie wordt gebruikt om relevantere en accuratere content te genereren</small>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Knowledgebase (Uitgebreid)</label>
                        <textarea id="website-knowledgebase" rows="10" placeholder="Voeg uitgebreide informatie toe:\n- Bedrijfsgeschiedenis\n- Producten en diensten details\n- USPs en voordelen\n- Belangrijke feiten en cijfers\n- Veelvoorkomende vragen\n- etc." style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; font-family: 'Courier New', monospace; resize: vertical;">${website.knowledgebase && typeof website.knowledgebase === 'object' ? JSON.stringify(website.knowledgebase, null, 2) : (website.knowledgebase || '')}</textarea>
                        <small style="color: #666; font-size: 12px;">Uitgebreide kennis die de AI kan gebruiken voor betere content. Je kunt hier alles kwijt wat belangrijk is voor je content.</small>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; border-left: 4px solid #2196f3;">
                        <p style="margin: 0; font-size: 13px; color: #1565c0; line-height: 1.6;">
                            <strong>💡 Tip:</strong> Hoe meer context je geeft, hoe beter de AI jouw bedrijf kan begrijpen en hoe relevanter de gegenereerde content zal zijn.
                        </p>
                    </div>
                </div>
            `;
            
        case 'links':
            const externalLinks = website.external_links || [];
            const linksHtml = externalLinks.map((link, i) => `
                <div class="external-link-item" style="display: flex; gap: 10px; margin-bottom: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px;">
                    <input type="url" class="external-link-url" placeholder="https://example.com/page" value="${link.url || ''}" style="flex: 2; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                    <input type="text" class="external-link-anchor" placeholder="Anchor tekst" value="${link.anchor || ''}" style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
                    <button type="button" onclick="this.closest('.external-link-item').remove()" style="padding: 10px 16px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; transition: all 0.3s;" onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'">🗑️</button>
                </div>
            `).join('');
            
            return `
                <div id="tab-content-links" class="tab-content">
                    <h4 style="margin: 0 0 8px 0; color: var(--dark-blue); font-size: 18px;">Externe Links</h4>
                    <p style="margin: 0 0 20px 0; font-size: 14px; color: #666;">Links die automatisch in je artikelen kunnen worden opgenomen</p>
                    
                    <div id="external-links-container" style="margin-bottom: 16px;">
                        ${linksHtml || '<p style="color: #999; text-align: center; padding: 20px;">Nog geen externe links toegevoegd</p>'}
                    </div>
                    
                    <button type="button" onclick="addExternalLink()" style="width: 100%; padding: 12px; background: #10b981; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.3s;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10b981'">
                        ➕ Nieuwe Link Toevoegen
                    </button>
                    
                    <div style="margin-top: 20px; background: #fef3c7; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <p style="margin: 0; font-size: 13px; color: #92400e; line-height: 1.6;">
                            <strong>💡 Tip:</strong> Deze links kunnen automatisch in je content worden verwerkt. Perfect voor affiliate links, product pages, of belangrijke landingspagina's.
                        </p>
                    </div>
                </div>
            `;
            
        case 'schedule':
            return `
                <div id="tab-content-schedule" class="tab-content">
                    <h4 style="margin: 0 0 20px 0; color: var(--dark-blue); font-size: 18px;">Posting Planning</h4>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Posting Schema *</label>
                        <select id="posting-schedule" required style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;" onchange="updatePostingDaysVisibility()">
                            <option value="daily" ${(website.posting_schedule || 'weekly') === 'daily' ? 'selected' : ''}>Dagelijks</option>
                            <option value="5x_week" ${website.posting_schedule === '5x_week' ? 'selected' : ''}>5x per week</option>
                            <option value="3x_week" ${website.posting_schedule === '3x_week' ? 'selected' : ''}>3x per week</option>
                            <option value="weekly" ${website.posting_schedule === 'weekly' ? 'selected' : ''}>Wekelijks</option>
                            <option value="monthly" ${website.posting_schedule === 'monthly' ? 'selected' : ''}>Maandelijks</option>
                        </select>
                    </div>
                    
                    <div id="posting-days-section" style="margin-bottom: 20px; display: none;">
                        <label style="display: block; margin-bottom: 12px; font-weight: 600; color: var(--dark-blue);">Posting Dagen</label>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px;">
                            ${['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day, i) => {
                                const dayNames = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag'];
                                const isChecked = Array.isArray(website.posting_days) && website.posting_days.includes(day);
                                return `
                                    <label style="display: flex; align-items: center; gap: 8px; padding: 12px; background: ${isChecked ? '#e0f2fe' : '#f8f9fa'}; border: 2px solid ${isChecked ? '#0ea5e9' : '#e0e0e0'}; border-radius: 8px; cursor: pointer; transition: all 0.3s;">
                                        <input type="checkbox" name="posting-day" value="${day}" ${isChecked ? 'checked' : ''} style="width: 18px; height: 18px;">
                                        <span style="font-size: 14px; font-weight: 600;">${dayNames[i]}</span>
                                    </label>
                                `;
                            }).join('')}
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Posting Tijd *</label>
                        <input type="time" id="posting-time" value="${website.posting_time || '09:00'}" required style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: flex; align-items: center; gap: 12px; padding: 18px; background: ${website.auto_publish ? '#d1fae5' : '#f8f9fa'}; border: 2px solid ${website.auto_publish ? '#10b981' : '#e0e0e0'}; border-radius: 12px; cursor: pointer; transition: all 0.3s;">
                            <input type="checkbox" id="auto-publish" ${website.auto_publish ? 'checked' : ''} style="width: 22px; height: 22px;">
                            <div style="flex: 1;">
                                <div style="font-weight: 700; color: var(--dark-blue); margin-bottom: 4px; font-size: 15px;">🤖 Automatisch Publiceren</div>
                                <div style="font-size: 13px; color: #666; line-height: 1.5;">Artikelen worden automatisch naar WordPress gepubliceerd volgens het schema</div>
                            </div>
                        </label>
                    </div>
                    
                    ${website.last_post_date ? `
                        <div style="background: #e8f5e9; padding: 14px; border-radius: 8px; border-left: 4px solid #10b981;">
                            <p style="margin: 0; font-size: 13px; color: #2e7d32;">
                                ✅ <strong>Laatste post:</strong> ${new Date(website.last_post_date).toLocaleDateString('nl-NL', { year: 'numeric', month: 'long', day: 'numeric' })}
                            </p>
                        </div>
                    ` : `
                        <div style="background: #fff3e0; padding: 14px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                            <p style="margin: 0; font-size: 13px; color: #e65100;">
                                ⏳ <strong>Nog geen posts gepubliceerd</strong>
                            </p>
                        </div>
                    `}
                </div>
            `;
            
        case 'wordpress':
            return `
                <div id="tab-content-wordpress" class="tab-content">
                    <h4 style="margin: 0 0 20px 0; color: var(--dark-blue); font-size: 18px;">WordPress Integratie</h4>
                    
                    ${website.wordpress_url ? `
                        <div style="background: #e8f5e9; padding: 16px; border-radius: 8px; border-left: 4px solid #10b981; margin-bottom: 20px;">
                            <p style="margin: 0; font-size: 14px; color: #2e7d32;">
                                ✅ <strong>WordPress verbonden</strong>
                            </p>
                        </div>
                    ` : `
                        <div style="background: #fff3e0; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 20px;">
                            <p style="margin: 0; font-size: 14px; color: #e65100;">
                                ⚠️ <strong>WordPress nog niet verbonden</strong> - Voeg credentials toe om automatisch te publiceren
                            </p>
                        </div>
                    `}
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">WordPress URL</label>
                        <input type="url" id="wordpress-url" value="${website.wordpress_url || ''}" placeholder="https://jouwwebsite.nl" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                        <small style="color: #666; font-size: 12px;">De hoofdURL van je WordPress website</small>
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">WordPress Username</label>
                        <input type="text" id="wordpress-username" value="${website.wordpress_username || ''}" placeholder="admin" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                    </div>
                    
                    <div style="margin-bottom: 20px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 600; color: var(--dark-blue);">Application Password</label>
                        <input type="password" id="wordpress-password" value="${website.wordpress_password || ''}" placeholder="xxxx xxxx xxxx xxxx" style="width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px;">
                        <small style="color: #666; font-size: 12px;">Genereer een Application Password in je WordPress admin (Gebruikers → Profiel)</small>
                    </div>
                    
                    <div style="background: #e3f2fd; padding: 16px; border-radius: 8px; border-left: 4px solid #2196f3;">
                        <p style="margin: 0 0 10px 0; font-size: 13px; color: #1565c0; line-height: 1.6;">
                            <strong>📖 WordPress Application Password Aanmaken:</strong>
                        </p>
                        <ol style="margin: 0; padding-left: 20px; font-size: 13px; color: #1565c0; line-height: 1.8;">
                            <li>Log in op je WordPress admin</li>
                            <li>Ga naar Gebruikers → Profiel</li>
                            <li>Scroll naar beneden naar "Application Passwords"</li>
                            <li>Voer een naam in (bijv. "WritgoAI") en klik op "Add New Application Password"</li>
                            <li>Kopieer het gegenereerde wachtwoord en plak het hier</li>
                        </ol>
                    </div>
                </div>
            `;
            
        default:
            return '<p>Unknown tab</p>';
    }
}

function switchTab(tab, websiteId) {
    currentTab = tab;
    
    // Update tab buttons
    document.querySelectorAll('.mgmt-tab').forEach(btn => {
        btn.style.color = '#666';
        btn.style.borderBottom = '3px solid transparent';
    });
    
    const activeBtn = document.getElementById(`tab-${tab}`);
    if (activeBtn) {
        activeBtn.style.color = '#667eea';
        activeBtn.style.borderBottom = '3px solid #667eea';
    }
    
    // Fetch current data and render tab content
    fetch(`/api/websites/${websiteId}/management`)
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const formContent = document.querySelector('#website-management-form > div');
                formContent.innerHTML = renderTabContent(tab, data.website, websiteId);
                
                // Initialize posting days visibility if on schedule tab
                if (tab === 'schedule') {
                    updatePostingDaysVisibility();
                }
            }
        })
        .catch(error => {
            console.error('Error switching tab:', error);
        });
}

function updateActiveTab(tab) {
    document.querySelectorAll('.mgmt-tab').forEach(btn => {
        btn.style.color = '#666';
        btn.style.borderBottom = '3px solid transparent';
    });
    
    const activeBtn = document.getElementById(`tab-${tab}`);
    if (activeBtn) {
        activeBtn.style.color = '#667eea';
        activeBtn.style.borderBottom = '3px solid #667eea';
    }
}

function updatePostingDaysVisibility() {
    const schedule = document.getElementById('posting-schedule')?.value;
    const daysSection = document.getElementById('posting-days-section');
    
    if (daysSection && schedule) {
        if (['3x_week', '5x_week', 'weekly'].includes(schedule)) {
            daysSection.style.display = 'block';
        } else {
            daysSection.style.display = 'none';
        }
    }
}

function addExternalLink() {
    const container = document.getElementById('external-links-container');
    
    // Remove empty message if exists
    const emptyMsg = container.querySelector('p');
    if (emptyMsg && emptyMsg.textContent.includes('Nog geen externe links')) {
        emptyMsg.remove();
    }
    
    const linkItem = document.createElement('div');
    linkItem.className = 'external-link-item';
    linkItem.style.cssText = 'display: flex; gap: 10px; margin-bottom: 12px; padding: 12px; background: #f8f9fa; border-radius: 8px;';
    linkItem.innerHTML = `
        <input type="url" class="external-link-url" placeholder="https://example.com/page" style="flex: 2; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
        <input type="text" class="external-link-anchor" placeholder="Anchor tekst" style="flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px;">
        <button type="button" onclick="this.closest('.external-link-item').remove()" style="padding: 10px 16px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; transition: all 0.3s;" onmouseover="this.style.background='#dc2626'" onmouseout="this.style.background='#ef4444'">🗑️</button>
    `;
    
    container.appendChild(linkItem);
}

function closeWebsiteManagementModal() {
    const modal = document.getElementById('website-management-modal');
    if (modal) {
        modal.remove();
    }
}

async function saveWebsiteManagement(event, websiteId) {
    event.preventDefault();
    
    try {
        // Collect data from all tabs
        const data = {};
        
        // Basic info
        const name = document.getElementById('website-name')?.value;
        const niche = document.getElementById('website-niche')?.value;
        const audience = document.getElementById('website-audience')?.value;
        const tone = document.getElementById('website-tone')?.value;
        
        if (name) data.name = name;
        if (niche) data.niche = niche;
        if (audience) data.target_audience = audience;
        if (tone) data.tone_of_voice = tone;
        
        // Context
        const context = document.getElementById('website-context')?.value;
        const knowledgebase = document.getElementById('website-knowledgebase')?.value;
        
        if (context !== undefined) data.context = context;
        if (knowledgebase !== undefined) data.knowledgebase = knowledgebase;
        
        // External links
        const linkItems = document.querySelectorAll('.external-link-item');
        if (linkItems.length > 0) {
            const links = [];
            linkItems.forEach(item => {
                const url = item.querySelector('.external-link-url')?.value;
                const anchor = item.querySelector('.external-link-anchor')?.value;
                if (url) {
                    links.push({ url, anchor: anchor || '' });
                }
            });
            data.external_links = links;
        }
        
        // Schedule
        const schedule = document.getElementById('posting-schedule')?.value;
        const time = document.getElementById('posting-time')?.value;
        const autoPublish = document.getElementById('auto-publish')?.checked;
        
        if (schedule) data.posting_schedule = schedule;
        if (time) data.posting_time = time;
        if (autoPublish !== undefined) data.auto_publish = autoPublish;
        
        // Posting days
        if (['3x_week', '5x_week', 'weekly'].includes(schedule)) {
            const checkedDays = document.querySelectorAll('input[name="posting-day"]:checked');
            const days = Array.from(checkedDays).map(cb => cb.value);
            if (days.length > 0) {
                data.posting_days = days;
            }
        }
        
        // WordPress
        const wpUrl = document.getElementById('wordpress-url')?.value;
        const wpUsername = document.getElementById('wordpress-username')?.value;
        const wpPassword = document.getElementById('wordpress-password')?.value;
        
        if (wpUrl) data.wordpress_url = wpUrl;
        if (wpUsername) data.wordpress_username = wpUsername;
        if (wpPassword) data.wordpress_password = wpPassword;
        
        // Save to API
        const response = await fetch(`/api/websites/${websiteId}/management`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('✅ Website instellingen opgeslagen!', 'success');
            closeWebsiteManagementModal();
            
            // Reload automation settings if on that view
            if (typeof loadAutomationSettings === 'function') {
                loadAutomationSettings();
            }
        } else {
            showNotification('Fout: ' + (result.error || 'Unknown error'), 'error');
        }
        
    } catch (error) {
        console.error('Error saving website management:', error);
        showNotification('Fout bij opslaan: ' + error.message, 'error');
    }
}

// Replace old function name with new one
window.openAutomationSettingsModal = openWebsiteManagementModal;
