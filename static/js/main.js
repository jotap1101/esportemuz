// EsporteMuz - Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize modals
    initializeModals();
    
    // Setup CSRF token for AJAX
    setupCSRFToken();
    
    // Setup form validations
    setupFormValidations();
    
    // Setup match result handlers
    setupMatchResultHandlers();
    
    // Setup team management
    setupTeamManagement();
    
    // Setup filters
    setupFilters();
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize Bootstrap modals
function initializeModals() {
    const modalElements = document.querySelectorAll('.modal');
    modalElements.forEach(modalEl => {
        modalEl.addEventListener('hidden.bs.modal', function() {
            // Clear form data when modal is closed
            const forms = modalEl.querySelectorAll('form');
            forms.forEach(form => form.reset());
        });
    });
}

// Setup CSRF token for AJAX requests
function setupCSRFToken() {
    // Try to get CSRF token from multiple sources
    let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    if (!csrfToken) {
        // Try to get from meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            csrfToken = metaTag.getAttribute('content');
        }
    }
    
    if (!csrfToken) {
        // Try to get from cookie
        csrfToken = getCookie('csrftoken');
    }
    
    if (csrfToken) {
        window.csrfToken = csrfToken;
    }
}

// Helper function to get cookie value
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Form validation setup
function setupFormValidations() {
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Match result handlers
function setupMatchResultHandlers() {
    // Result registration modal
    const resultButtons = document.querySelectorAll('.btn-register-result');
    resultButtons.forEach(button => {
        button.addEventListener('click', function() {
            const matchId = this.dataset.matchId;
            const mandante = this.dataset.mandante;
            const visitante = this.dataset.visitante;
            
            openResultModal(matchId, mandante, visitante);
        });
    });
    
    // Result form submission
    const resultForm = document.getElementById('resultForm');
    if (resultForm) {
        resultForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitMatchResult();
        });
    }
}

// Open result registration modal
function openResultModal(matchId, mandante, visitante) {
    const modal = document.getElementById('resultModal');
    const modalTitle = modal.querySelector('.modal-title');
    const matchIdInput = modal.querySelector('#matchId');
    
    modalTitle.textContent = `${mandante} x ${visitante}`;
    matchIdInput.value = matchId;
    
    // Reset form
    modal.querySelector('#golsMandante').value = '';
    modal.querySelector('#golsVisitante').value = '';
    
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

// Submit match result via AJAX
async function submitMatchResult() {
    const form = document.getElementById('resultForm');
    const formData = new FormData(form);
    
    const data = {
        partida_id: formData.get('matchId'),
        gols_mandante: formData.get('golsMandante'),
        gols_visitante: formData.get('golsVisitante')
    };
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/registrar-resultado/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('success', result.message);
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('resultModal'));
            modal.hide();
            // Reload page to show updated data
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('error', result.message);
        }
    } catch (error) {
        showAlert('error', 'Erro ao registrar resultado. Tente novamente.');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

// Team management setup
function setupTeamManagement() {
    // Add team to championship
    const addTeamButtons = document.querySelectorAll('.btn-add-team');
    addTeamButtons.forEach(button => {
        button.addEventListener('click', function() {
            const championshipId = this.dataset.championshipId;
            openAddTeamModal(championshipId);
        });
    });
    
    // Team selection in modal
    const teamSelect = document.getElementById('teamSelect');
    if (teamSelect) {
        setupTeamSearch(teamSelect);
    }

    // Add team button handler
    const addTeamBtn = document.getElementById('addTeamBtn');
    if (addTeamBtn) {
        addTeamBtn.addEventListener('click', function() {
            const championshipId = document.getElementById('addTeamModal').dataset.championshipId;
            const teamId = document.getElementById('teamSelect').value;
            
            if (championshipId && teamId) {
                addTeamToChampionship(championshipId, teamId);
            }
        });
    }
}

// Setup team search functionality
function setupTeamSearch(selectElement) {
    selectElement.addEventListener('change', function() {
        const selectedTeam = this.value;
        const addButton = document.getElementById('addTeamBtn');
        if (addButton) {
            addButton.disabled = !selectedTeam;
        }
    });
}

// Open add team modal
function openAddTeamModal(championshipId) {
    const modal = document.getElementById('addTeamModal');
    const teamSelect = document.getElementById('teamSelect');
    
    // Store championship ID in modal
    modal.dataset.championshipId = championshipId;
    
    // Clear and load teams
    teamSelect.innerHTML = '<option value="">Carregando...</option>';
    
    // Load available teams
    loadAvailableTeams(championshipId, teamSelect);
    
    // Show modal
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

// Load teams not in championship
async function loadAvailableTeams(championshipId, selectElement) {
    try {
        const response = await fetch(`/api/equipes/?campeonato_id=${championshipId}`);
        const data = await response.json();
        
        // Clear options
        selectElement.innerHTML = '<option value="">Escolha uma equipe...</option>';
        
        // Add teams
        if (data.equipes && data.equipes.length > 0) {
            data.equipes.forEach(team => {
                const option = document.createElement('option');
                option.value = team.id;
                option.textContent = `${team.nome} - ${team.cidade}`;
                selectElement.appendChild(option);
            });
        } else {
            selectElement.innerHTML = '<option value="">Nenhuma equipe disponível</option>';
        }
        
        // Reset add button
        const addButton = document.getElementById('addTeamBtn');
        if (addButton) {
            addButton.disabled = true;
        }
        
    } catch (error) {
        console.error('Error loading teams:', error);
        selectElement.innerHTML = '<option value="">Erro ao carregar equipes</option>';
    }
}

// Add team to championship
async function addTeamToChampionship(championshipId, teamId) {
    const data = {
        campeonato_id: championshipId,
        equipe_id: teamId
    };
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/adicionar-equipe-campeonato/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.csrfToken
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert('success', result.message);
            setTimeout(() => location.reload(), 1000);
        } else {
            showAlert('error', result.message);
        }
    } catch (error) {
        showAlert('error', 'Erro ao adicionar equipe. Tente novamente.');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

// Remove team from championship
async function removeTeam(participacaoId) {
    const confirmation = await Swal.fire({
        title: 'Remover Equipe',
        text: 'Tem certeza que deseja remover esta equipe do campeonato?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sim, remover',
        cancelButtonText: 'Cancelar'
    });
    
    if (confirmation.isConfirmed) {
        showLoading(true);
        
        try {
            const response = await fetch(`/api/remover-equipe-campeonato/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': window.csrfToken
                },
                body: JSON.stringify({
                    participacao_id: participacaoId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAlert('success', result.message);
                setTimeout(() => location.reload(), 1000);
            } else {
                showAlert('error', result.message);
            }
        } catch (error) {
            showAlert('error', 'Erro ao remover equipe. Tente novamente.');
            console.error('Error:', error);
        } finally {
            showLoading(false);
        }
    }
}

// Setup filters
function setupFilters() {
    // Auto-submit filters on change
    const filterForms = document.querySelectorAll('.filter-form');
    filterForms.forEach(form => {
        const selects = form.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', function() {
                form.submit();
            });
        });
    });
    
    // Clear filters button
    const clearFilterButtons = document.querySelectorAll('.btn-clear-filters');
    clearFilterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            const inputs = form.querySelectorAll('input, select');
            inputs.forEach(input => {
                if (input.type === 'text' || input.type === 'search') {
                    input.value = '';
                } else if (input.tagName === 'SELECT') {
                    input.selectedIndex = 0;
                }
            });
            form.submit();
        });
    });
}

// Generate championship rounds
async function generateRounds(championshipId) {
    const confirmation = await Swal.fire({
        title: 'Gerar Rodadas',
        text: 'Tem certeza que deseja gerar as rodadas? Rodadas existentes serão substituídas.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Sim, gerar',
        cancelButtonText: 'Cancelar'
    });
    
    if (confirmation.isConfirmed) {
        showLoading(true);
        
        try {
            const response = await fetch(`/campeonatos/${championshipId}/gerar-rodadas/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': window.csrfToken
                }
            });
            
            if (response.ok) {
                showAlert('success', 'Rodadas geradas com sucesso!');
                setTimeout(() => location.reload(), 1000);
            } else {
                showAlert('error', 'Erro ao gerar rodadas.');
            }
        } catch (error) {
            showAlert('error', 'Erro ao gerar rodadas. Tente novamente.');
            console.error('Error:', error);
        } finally {
            showLoading(false);
        }
    }
}

// Refresh classification table
async function refreshClassification(championshipId, group = null) {
    showLoading(true);
    
    try {
        let url = `/api/classificacao/${championshipId}/`;
        if (group) {
            url += `?grupo=${group}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.classificacao) {
            updateClassificationTable(data.classificacao, group);
        }
    } catch (error) {
        console.error('Error refreshing classification:', error);
    } finally {
        showLoading(false);
    }
}

// Update classification table
function updateClassificationTable(classification, group = null) {
    const tableId = group ? `classification-table-${group}` : 'classification-table';
    const table = document.getElementById(tableId);
    
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    tbody.innerHTML = '';
    
    classification.forEach((item, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="position">${index + 1}</td>
            <td class="team-name">${item.equipe}</td>
            <td>${item.pontos}</td>
            <td>${item.jogos}</td>
            <td>${item.vitorias}</td>
            <td>${item.empates}</td>
            <td>${item.derrotas}</td>
            <td>${item.gols_pro}</td>
            <td>${item.gols_contra}</td>
            <td>${item.saldo_gols}</td>
        `;
        tbody.appendChild(row);
    });
}

// Utility functions
function showLoading(show) {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) {
        spinner.classList.toggle('d-none', !show);
    }
}

function showAlert(type, message) {
    Swal.fire({
        icon: type,
        title: type === 'success' ? 'Sucesso!' : 'Erro!',
        text: message,
        timer: 3000,
        showConfirmButton: false
    });
}

// Export functions for global use
window.EsporteMuz = {
    generateRounds,
    refreshClassification,
    addTeamToChampionship,
    removeTeam,
    showAlert,
    showLoading
};

// Make removeTeam globally accessible for onclick handlers
window.removeTeam = removeTeam;
