document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('searchForm');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsList = document.getElementById('resultsList');
    const loadingSpinner = document.getElementById('loadingSpinner');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        loadingSpinner.classList.remove('d-none');
        resultsList.innerHTML = '';
        
        const searchData = {
            position: document.getElementById('position').value,
            experience: document.getElementById('experience').value,
            salary: document.getElementById('salary').value,
            jobNature: document.getElementById('jobNature').value,
            location: document.getElementById('location').value,
            skills: document.getElementById('skills').value
        };

        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(searchData)
            });

            const data = await response.json();
            
            if (data.jobs && data.jobs.length > 0) {
                displayResults(data.jobs);
            } else {
                resultsList.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle me-2"></i>
                        No jobs found matching your criteria. Try adjusting your search parameters.
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error:', error);
            resultsList.innerHTML = `
                <div class="alert alert-info">
                    <i class="fas fa-info-circle me-2"></i>
                    No jobs found matching your criteria. Try adjusting your search parameters.
                </div>
            `;
        } finally {
            loadingSpinner.classList.add('d-none');
        }
    });

    function displayResults(jobs) {
        resultsList.innerHTML = jobs.map(job => `
            <div class="job-card mb-3">
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start">
                            <h5 class="card-title">${job.job_title || 'Position Not Specified'}</h5>
                            <span class="match-score">
                                ${Math.round(job.match_score)}% Match
                            </span>
                        </div>
                        <h6 class="card-subtitle mb-2 text-muted">
                            <i class="fas fa-building me-2"></i>${job.company || 'Company Not Specified'}
                        </h6>
                        <div class="job-details mb-3">
                            <span class="me-3">
                                <i class="fas fa-map-marker-alt me-1"></i>${job.location || 'Location Not Specified'}
                            </span>
                            <span class="me-3">
                                <i class="fas fa-briefcase me-1"></i>${job.experience || 'Experience Not Specified'}
                            </span>
                            <span>
                                <i class="fas fa-money-bill-wave me-1"></i>${job.salary || 'Salary Not Specified'}
                            </span>
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="source">
                                <i class="fas fa-globe me-1"></i>${job.source}
                            </span>
                            <a href="${job.apply_link}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-external-link-alt me-1"></i>Apply Now
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
}); 