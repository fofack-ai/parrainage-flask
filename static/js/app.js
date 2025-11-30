// Configuration API - Flask
const API_BASE_URL = '/api';

// Gestion de l'inscription
document.getElementById("signupForm")?.addEventListener("submit", async function(e){
    e.preventDefault();
    
    const submitBtn = document.getElementById("submitBtn");
    const loading = document.getElementById("loading");
    
    const formData = {
        nom: document.getElementById("nom").value.trim(),
        matricule: document.getElementById("matricule").value.trim(),
        password: document.getElementById("password").value,
        serie: document.getElementById("serie").value
    };
    
    // Validation
    if (formData.password !== document.getElementById("confirmPassword").value) {
        alert("❌ Les mots de passe ne correspondent pas !");
        return;
    }
    
    if (formData.password.length < 4) {
        alert("❌ Le mot de passe doit contenir au moins 4 caractères !");
        return;
    }
    
    if (!formData.serie) {
        alert("❌ Veuillez sélectionner votre série !");
        return;
    }
    
    // Loading
    submitBtn.disabled = true;
    submitBtn.textContent = "Inscription en cours...";
    loading.classList.remove("hidden");
    
    try {
        const response = await fetch(`${API_BASE_URL}/signup`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.parrain) {
                showParrainModal(result.parrain, formData.serie);
            } else {
                alert("✅ " + result.message);
                window.location.href = "/login";
            }
            
            localStorage.setItem('user', JSON.stringify(result.user));
            if (result.parrain) {
                localStorage.setItem('parrain', JSON.stringify(result.parrain));
            }
            
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert("❌ Erreur de connexion au serveur");
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "S'inscrire et trouver mon parrain";
        loading.classList.add("hidden");
    }
});

// Gestion de la connexion
document.getElementById("loginForm")?.addEventListener("submit", async function(e){
    e.preventDefault();
    
    const formData = {
        nom: document.getElementById("nom").value.trim(),
        matricule: document.getElementById("matricule").value.trim(),
        password: document.getElementById("password").value
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            localStorage.setItem('user', JSON.stringify(result.user));
            if (result.parrain) {
                localStorage.setItem('parrain', JSON.stringify(result.parrain));
            }
            window.location.href = "/dashboard";
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert("❌ Erreur de connexion au serveur");
    }
});

// Afficher le modal parrain
function showParrainModal(parrain, serieFilleul) {
    const modal = document.getElementById("parrainModal");
    
    document.getElementById("parrainName").textContent = parrain.nom;
    document.getElementById("parrainSerie").textContent = serieFilleul;
    document.getElementById("parrainSerieText").textContent = parrain.serie;
    document.getElementById("parrainMatricule").textContent = parrain.matricule;
    
    // Photo du parrain
    const photoEl = document.getElementById("parrainImage");
    photoEl.src = parrain.photo || 'https://via.placeholder.com/100?text=Photo';
    
    // Lien WhatsApp
    const whatsappLink = document.getElementById("parrainWhatsapp");
    const phone = parrain.telephone || '';
    if (phone) {
        const whatsappUrl = `https://wa.me/${phone.replace(/\D/g, '')}`;
        whatsappLink.href = whatsappUrl;
        document.getElementById("parrainPhone").textContent = phone;
    } else {
        whatsappLink.style.display = 'none';
    }
    
    modal.classList.remove("hidden");
    
    document.getElementById("goToDashboard").onclick = function() {
        window.location.href = "/dashboard";
    };
    
    document.getElementById("closeModal").onclick = function() {
        modal.classList.add("hidden");
    };
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.classList.add("hidden");
        }
    };
}

// Dashboard
if (window.location.pathname.includes('/dashboard')) {
    document.addEventListener('DOMContentLoaded', function() {
        const user = JSON.parse(localStorage.getItem('user'));
        const parrain = JSON.parse(localStorage.getItem('parrain'));
        
        if (!user) {
            window.location.href = '/login';
            return;
        }
        
        document.getElementById('userName').textContent = user.nom;
        
        if (user.niveau === '1') {
            showFilleulView(parrain);
        } else {
            showParrainView(user.id);
        }
        
        document.getElementById('logoutBtn').addEventListener('click', function() {
            localStorage.clear();
            window.location.href = '/';
        });
    });
}

function showFilleulView(parrain) {
    document.getElementById('filleulView').classList.remove('hidden');
    const parrainInfo = document.getElementById('parrainInfo');
    
    if (parrain) {
        const whatsappUrl = parrain.telephone ? `https://wa.me/${parrain.telephone.replace(/\D/g, '')}` : '#';
        
        parrainInfo.innerHTML = `
            <div class="parrain-display">
                <img src="${parrain.photo || 'https://via.placeholder.com/80?text=Photo'}" alt="Photo de ${parrain.nom}">
                <div class="parrain-details">
                    <h3>${parrain.nom}</h3>
                    <p><strong>📞 WhatsApp :</strong> 
                        <a href="${whatsappUrl}" target="_blank" class="whatsapp-link">
                            ${parrain.telephone || 'Non renseigné'}
                        </a>
                    </p>
                    <p><strong>🎓 Série :</strong> ${parrain.serie}</p>
                    <p><strong>📧 Matricule :</strong> ${parrain.matricule}</p>
                </div>
            </div>
        `;
    } else {
        parrainInfo.innerHTML = `
            <p class="no-parrain">⏳ Recherche d'un parrain en cours...</p>
            <p><small>Vous serez notifié dès qu'un parrain sera disponible</small></p>
        `;
    }
}

async function showParrainView(parrainId) {
    document.getElementById('parrainView').classList.remove('hidden');
    
    try {
        const response = await fetch(`${API_BASE_URL}/parrain/${parrainId}`);
        const result = await response.json();
        
        const filleulInfo = document.getElementById('filleulInfo');
        
        if (result.success && result.filleul) {
            filleulInfo.innerHTML = `
                <div class="filleul-display">
                    <h3>${result.filleul.nom}</h3>
                    <p><strong>📧 Matricule :</strong> ${result.filleul.matricule}</p>
                    <p><strong>🎓 Série :</strong> ${result.filleul.serie}</p>
                    <p><strong>📅 Inscription :</strong> ${new Date(result.filleul.date_inscription).toLocaleDateString()}</p>
                </div>
            `;
        } else {
            filleulInfo.innerHTML = `
                <p class="no-filleul">👤 En attente d'un filleul...</p>
                <p><small>Les élèves de 1ère année seront automatiquement attribués</small></p>
            `;
        }
    } catch (error) {
        console.error('Erreur:', error);
    }
}