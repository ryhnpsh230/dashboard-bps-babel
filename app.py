let isScraping = false;
let allScrapedData = [];
let currentPage = 1;

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "START_SCRAPING" && !isScraping) {
        isScraping = true;
        allScrapedData = [];
        currentPage = 1;
        injectFloatingUI();
        runBot();
    }
});

function injectFloatingUI() {
    if (document.getElementById('bps-scraper-ui')) return;
    
    const bpsLogoUrl = chrome.runtime.getURL('logo.png');
    
    let style = document.createElement('style');
    style.innerHTML = `
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono&family=DM+Sans:wght@500;700&display=swap');
        
        @keyframes pulse-neon {
            0% { box-shadow: 0 0 2px #00d2ff; }
            50% { box-shadow: 0 0 10px #00d2ff; }
            100% { box-shadow: 0 0 2px #00d2ff; }
        }

        .bps-panel {
            position: fixed; bottom: 25px; left: 25px; width: 320px; 
            background: rgba(6, 16, 31, 0.95);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(0, 210, 255, 0.3);
            border-radius: 12px; 
            padding: 18px; 
            box-shadow: 0 12px 40px rgba(0,0,0,0.8); 
            z-index: 2147483647;
            font-family: 'DM Sans', sans-serif; 
            color: #dbeafe;
        }

        .bps-header {
            display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 15px; border-bottom: 1px solid rgba(56, 139, 255, 0.2);
            padding-bottom: 10px;
        }

        .bps-title { 
            display: flex; align-items: center; gap: 8px;
            font-weight: 700; font-size: 14px; color: #fff; letter-spacing: 0.5px; 
        }

        .bps-logo-img {
            width: 18px; height: 18px; object-fit: contain;
            filter: drop-shadow(0 0 3px rgba(0, 210, 255, 0.8));
        }
        
        .bps-badge {
            font-family: 'DM Mono', monospace; font-size: 9px;
            background: rgba(0, 210, 255, 0.15); color: #00d2ff;
            padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(0, 210, 255, 0.4);
        }

        .bps-stat-grid {
            display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;
        }

        .bps-stat-card {
            background: rgba(16, 32, 64, 0.6); padding: 10px; border-radius: 8px;
            border: 1px solid rgba(56, 139, 255, 0.15); text-align: center;
        }

        .bps-stat-label { font-size: 9px; text-transform: uppercase; color: #6b8cba; letter-spacing: 1px; margin-bottom: 4px; }
        .bps-stat-value { font-family: 'DM Mono', monospace; font-size: 20px; font-weight: 500; color: #fff; }

        .bps-progress-container {
            height: 6px; background: rgba(255,255,255,0.1); border-radius: 10px;
            overflow: hidden; margin-bottom: 15px; position: relative;
        }

        .bps-progress-bar {
            height: 100%; width: 0%; background: linear-gradient(90deg, #1a6fff, #00d2ff);
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.6); transition: width 0.4s ease;
        }

        .bps-status-text { font-size: 11px; color: #38bdf8; font-family: 'DM Mono', monospace; margin-bottom: 15px; display: block; line-height: 1.4;}

        .bps-btn-stop {
            width: 100%; padding: 12px; 
            background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
            color: white; border: none; border-radius: 8px; cursor: pointer; 
            font-weight: 700; font-size: 13px; transition: 0.3s;
            box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
            text-transform: uppercase; letter-spacing: 1px;
        }

        .bps-btn-stop:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(239, 68, 68, 0.5); filter: brightness(1.1); }
    `;
    document.head.appendChild(style);

    let ui = document.createElement('div');
    ui.id = 'bps-scraper-ui';
    ui.className = 'bps-panel';
    ui.innerHTML = `
        <div class="bps-header">
            <div class="bps-title">
                <img src="${bpsLogoUrl}" class="bps-logo-img" alt="BPS">
                BPS INTELLIGENCE
            </div>
            <div class="bps-badge">FAST MODE</div>
        </div>
        
        <div class="bps-stat-grid">
            <div class="bps-stat-card">
                <div class="bps-stat-label">Records Found</div>
                <div id="bps-count" class="bps-stat-value">0</div>
            </div>
            <div class="bps-stat-card">
                <div class="bps-stat-label">Current Page</div>
                <div id="bps-page-display" class="bps-stat-value">1</div>
            </div>
        </div>

        <div class="bps-progress-container">
            <div id="bps-progress-bar" class="bps-progress-bar"></div>
        </div>

        <span id="bps-percent" class="bps-status-text">> Mempersiapkan Pelacak...</span>

        <button id="bps-stop-btn" class="bps-btn-stop">
            ⏹ Abort & Compile Data
        </button>
    `;
    document.body.appendChild(ui);

    document.getElementById('bps-stop-btn').addEventListener('click', () => {
        isScraping = false;
        document.getElementById('bps-percent').innerText = "> Process aborted. Compiling CSV...";
        document.getElementById('bps-percent').style.color = "#ef4444";
        document.getElementById('bps-stop-btn').style.display = 'none';
        downloadCSV(allScrapedData);
    });
}

function updateUI(statusText) {
    let percentEl = document.getElementById('bps-percent');
    let countEl = document.getElementById('bps-count');
    let pageEl = document.getElementById('bps-page-display');
    let barEl = document.getElementById('bps-progress-bar');
    
    if (percentEl) percentEl.innerText = `> ${statusText}`;
    if (countEl) countEl.innerText = allScrapedData.length;
    
    if (window.location.href.includes("facebook")) {
        if (pageEl) pageEl.innerText = "∞"; 
    } else {
        if (pageEl) pageEl.innerText = currentPage;
    }
    
    if (barEl) {
        let progress = (currentPage * 10) % 105; 
        barEl.style.width = `${progress}%`;
    }

    try {
        chrome.runtime.sendMessage({
            action: "UPDATE_STATS",
            count: allScrapedData.length,
            page: window.location.href.includes("facebook") ? "∞" : currentPage
        });
    } catch (e) {}
}

const delay = (ms) => new Promise(res => setTimeout(res, ms));

async function extractDataTepatSasaran() {
    let results = [];
    let currentUrl = window.location.href;

    if (currentUrl.includes("shopee")) {
        let cards = document.querySelectorAll('a[data-sqe="link"], a.contents, li.col-xs-2-4 > a, div.contents > a');
        cards.forEach(card => {
            let nameEl = card.querySelector('.whitespace-normal');
            let priceEl = card.querySelector('.font-medium, .truncate + span'); 
            let locationEl = card.querySelector('.ml-\\[3px\\], .truncate.ml-\\[3px\\]') || card.querySelector('.mt-1 > .truncate');
            let name = nameEl ? nameEl.innerText : '';
            let price = priceEl ? priceEl.innerText : '';
            let location = locationEl ? locationEl.innerText : 'Tidak diketahui';
            let link = card.href || '';
            if (price && !price.toLowerCase().includes('rp')) price = "Rp" + price;
            let shopName = "Cari di Link"; 
            let storeType = card.innerHTML.includes('Star') || card.innerHTML.includes('Mall') ? 'Star/Mall' : 'Toko Reguler';
            
            if (name && price) {
                results.push({ "Nama Toko": shopName, "Nama Produk": name, "Wilayah": location, "Tipe Usaha": storeType, "Harga": price, "Link": link });
            }
        });

    } else if (currentUrl.includes("tokopedia")) {
        let cards = document.querySelectorAll('[data-testid="divProductWrapper"], [data-testid="master-product-card"]');
        
        if (cards.length === 0) {
            let allLinks = document.querySelectorAll('a[href*="tokopedia.com/"]');
            cards = Array.from(allLinks).filter(a => a.innerText.includes('Rp') && a.innerText.split('\n').length > 2);
        }

        cards.forEach(card => {
            let lines = card.innerText.split('\n').map(t => t.trim()).filter(t => t.length > 0);
            
            let name = "";
            let price = "";
            let location = "Tidak diketahui";
            let shopName = "Cek Link";
            
            let nameEl = card.querySelector('[data-testid="linkProductName"], [data-testid="spnSRPProdName"], .prd_link-product-name');
            let priceEl = card.querySelector('[data-testid="linkProductPrice"], [data-testid="spnSRPProdPrice"], .prd_link-product-price');
            let locEl = card.querySelector('[data-testid="linkShopLoc"], [data-testid="spnSRPProdTabShopLoc"], .prd_link-shop-loc');
            let shopEl = card.querySelector('[data-testid="linkShopName"], [data-testid="spnSRPProdTabShopName"], .prd_link-shop-name');
            
            if (nameEl && priceEl) {
                name = nameEl.innerText;
                price = priceEl.innerText;
                location = locEl ? locEl.innerText : location;
                shopName = shopEl ? shopEl.innerText : shopName;
            } else {
                name = lines[0]; 
                price = lines.find(t => t.includes('Rp')) || '';
                
                let priceIdx = lines.findIndex(t => t.includes('Rp'));
                if (priceIdx !== -1) {
                    let infoLines = lines.slice(priceIdx + 1).filter(t => 
                        !t.toLowerCase().includes('terjual') && 
                        !t.toLowerCase().includes('rb') && 
                        !t.toLowerCase().includes('rating') && 
                        !t.toLowerCase().includes('cashback') && 
                        !t.toLowerCase().includes('diskon') && 
                        !t.includes('%') && 
                        !t.toLowerCase().includes('grosir') &&
                        !t.toLowerCase().includes('sisa') &&
                        !t.toLowerCase().includes('preorder') &&
                        !/^[0-9.,]+$/.test(t) && 
                        t.length > 2
                    );
                    
                    if (infoLines.length >= 2) {
                        location = infoLines[infoLines.length - 1]; 
                        shopName = infoLines[infoLines.length - 2]; 
                    } else if (infoLines.length === 1) {
                        location = infoLines[0];
                    }
                }
            }
            
            let isOfficial = card.innerHTML.toLowerCase().includes('official') || card.innerHTML.toLowerCase().includes('pro') || card.querySelector('[data-testid="imgPromoBadge"]');
            let storeType = isOfficial ? 'Official Store/Pro' : 'Toko Reguler';
            let link = card.href || card.querySelector('a')?.href || '';

            if (name && price && name.trim() !== "") {
                results.push({ "Nama Toko": shopName, "Nama Produk": name, "Wilayah": location, "Tipe Usaha": storeType, "Harga": price, "Link": link });
            }
        });

    } else if (currentUrl.includes("facebook.com/marketplace")) {
        // --- LOGIKA FACEBOOK: FAST MODE (NGEBUT) ---
        let items = document.querySelectorAll('div[style*="max-width"], div[class*="x1i10hfl"] a[href*="/marketplace/item/"]');
        
        if (items.length === 0) {
            items = document.querySelectorAll('a[href*="/marketplace/item/"]');
        }

        for (let item of items) {
            if (!isScraping) break; 

            let container = item.closest('div[style*="max-width"]') || item.parentElement?.parentElement || item;
            let rawText = container.innerText || item.innerText || "";
            let lines = rawText.split('\n').map(t => t.trim()).filter(t => t.length > 0);
            
            if (lines.length >= 2) {
                let price = lines.find(t => t.includes('Rp') || t.match(/^[\d,.]+$/)) || lines[0];
                let name = lines.find(t => t !== price && t.length > 3) || lines[1] || "Produk FB";
                let locationIndex = lines.findIndex(t => t === name) + 1;
                let location = lines[locationIndex] || "Tidak diketahui";
                
                let linkElement = item.tagName === 'A' ? item : item.querySelector('a');
                if (!linkElement) continue; 
                
                let link = linkElement.href.startsWith('http') ? linkElement.href : window.location.origin + linkElement.getAttribute('href');

                if (allScrapedData.some(oldItem => oldItem.Link === link)) continue;

                if (name !== "Produk FB" && price.includes('Rp')) {
                    // LANGSUNG PUSH KE HASIL TANPA FETCH ATAU DELAY
                    results.push({ 
                        "Nama Toko": "Privasi (FB User)", 
                        "Nama Produk": name, 
                        "Wilayah": location, 
                        "Tipe Usaha": "Perorangan (Facebook)", 
                        "Harga": price, 
                        "Link": link 
                    });
                }
            }
        }
    }

    return results;
}

function downloadCSV(data) {
    if (data.length === 0) {
        alert("Data kosong. Silakan refresh halaman dan jalankan kembali.");
        return;
    }
    const headers = ["Nama Toko", "Nama Produk", "Wilayah", "Tipe Usaha", "Harga", "Link"];
    let csvContent = headers.join(",") + "\n";
    data.forEach(row => {
        let rowData = headers.map(header => {
            let cell = row[header] ? String(row[header]) : "";
            cell = cell.replace(/\r?\n|\r/g, " "); 
            cell = cell.replace(/,/g, " "); 
            cell = cell.replace(/"/g, ""); 
            return cell; 
        });
        csvContent += rowData.join(",") + "\n";
    });
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    
    let today = new Date();
    let dateString = `${today.getDate()}-${today.getMonth() + 1}-${today.getFullYear()}`;
    
    let marketplace = "Data";
    if (window.location.href.includes("tokopedia")) marketplace = "Tokopedia";
    else if (window.location.href.includes("shopee")) marketplace = "Shopee";
    else if (window.location.href.includes("facebook")) marketplace = "FB_Marketplace";
    
    a.download = `Data_BPS_${marketplace}_${dateString}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

async function runBot() {
    let currentUrl = window.location.href;

    while (isScraping) {
        let stuckCount = 0;
        
        while (isScraping) {
            window.scrollBy(0, 500); 
            await delay(800); // Ini jeda scroll ya bro, biar gambarnya sempet loading
            
            let pageData = await extractDataTepatSasaran();
            let newDataCount = 0;
            
            pageData.forEach(newItem => {
                if (!allScrapedData.some(oldItem => oldItem.Link === newItem.Link)) {
                    allScrapedData.push(newItem);
                    newDataCount++;
                }
            });

            if (currentUrl.includes("facebook")) updateUI(`Menarik Data... (+${newDataCount} baru)`);
            else updateUI(`Menyapu Hal ${currentPage}...`);

            let currentPosition = window.innerHeight + window.scrollY;
            let totalHeight = document.body.scrollHeight;

            if (currentPosition >= totalHeight - 300) {
                updateUI("Menunggu Produk Tambahan Terisi (Loading)...");
                await delay(2000); // Kalau mentok bawah, tunggu 2 detik biar FB ngeload produk baru
                
                let newHeight = document.body.scrollHeight;
                if (newHeight > totalHeight || newDataCount > 0) {
                    stuckCount = 0; 
                } else {
                    stuckCount++;
                    if (stuckCount >= 2) break; 
                }
            }
        }
        
        if (!isScraping) break; 
        
        if (currentUrl.includes("facebook")) {
            updateUI(`Data mentok sampai bawah. Selesai!`);
            isScraping = false; 
        } else {
            updateUI(`Mencari Tombol Selanjutnya...`);
            await delay(1500); 

            if (currentUrl.includes("shopee")) {
                let nextBtn = document.querySelector('.shopee-icon-button--right, button.shopee-button-outline:last-child'); 
                if (nextBtn && !nextBtn.disabled && !nextBtn.classList.contains('shopee-button-no-outline')) {
                    nextBtn.click();
                    currentPage++;
                    await delay(4000); 
                } else {
                    isScraping = false; 
                }
            } else if (currentUrl.includes("tokopedia")) {
                let allButtons = document.querySelectorAll('button');
                let loadMoreBtn = Array.from(allButtons).find(btn => btn.innerText.toLowerCase().includes('muat lebih banyak') || btn.innerText.toLowerCase().includes('tampilkan lebih banyak'));
                let nextBtn = document.querySelector('[aria-label="Laman berikutnya"], [aria-label="Halaman berikutnya"], [data-testid="btnSRPNextPage"]');

                if (loadMoreBtn && !loadMoreBtn.disabled) {
                    loadMoreBtn.click();
                    currentPage++;
                    await delay(4000);
                } else if (nextBtn && !nextBtn.disabled) {
                    nextBtn.click();
                    currentPage++;
                    await delay(4000); 
                } else {
                    isScraping = false;
                }
            }
        }
    }
    
    if (!isScraping && allScrapedData.length > 0) {
        updateUI("Pencarian Selesai & Mengemas Data");
        document.getElementById('bps-stop-btn').style.display = 'none';
        downloadCSV(allScrapedData);
    }
}
