/**
 * FixItFred Universal Project Tracker
 * Tracks deployments across all dashboards and provides project management
 */

class ProjectTracker {
    constructor() {
        this.projects = [];
        this.localStorage_key = 'fixitfred_projects';
        this.stats_key = 'fixitfred_stats';
        this.init();
    }

    init() {
        this.loadProjects();
        this.updateStats();
        
        // Listen for deployment events
        window.addEventListener('fixitfred:deployment', (event) => {
            this.addProject(event.detail);
        });
        
        // Listen for project updates
        window.addEventListener('fixitfred:project_update', (event) => {
            this.updateProject(event.detail.id, event.detail.updates);
        });
    }

    loadProjects() {
        try {
            const saved = localStorage.getItem(this.localStorage_key);
            if (saved) {
                this.projects = JSON.parse(saved);
            } else {
                // Initialize with demo projects
                this.projects = this.generateDemoProjects();
                this.saveProjects();
            }
        } catch (error) {
            console.error('Error loading projects:', error);
            this.projects = this.generateDemoProjects();
        }
    }

    saveProjects() {
        try {
            localStorage.setItem(this.localStorage_key, JSON.stringify(this.projects));
            this.updateStats();
        } catch (error) {
            console.error('Error saving projects:', error);
        }
    }

    addProject(projectData) {
        const project = {
            id: projectData.id || this.generateId(),
            company_name: projectData.company_name,
            industry: projectData.industry || 'general',
            icon: this.getIndustryIcon(projectData.industry),
            status: projectData.status || 'active',
            worker_count: projectData.worker_count || 100,
            revenue: projectData.revenue || 50000,
            modules: projectData.modules || ['operations', 'memory'],
            created_date: new Date().toISOString().split('T')[0],
            deployment_url: projectData.deployment_url || `https://${this.slugify(projectData.company_name)}.fixitfred.ai`,
            ...projectData
        };

        this.projects.push(project);
        this.saveProjects();
        
        // Notify other components
        this.dispatchEvent('project_added', project);
        
        return project;
    }

    updateProject(id, updates) {
        const index = this.projects.findIndex(p => p.id === id);
        if (index !== -1) {
            this.projects[index] = { ...this.projects[index], ...updates };
            this.saveProjects();
            this.dispatchEvent('project_updated', this.projects[index]);
        }
    }

    getProject(id) {
        return this.projects.find(p => p.id === id);
    }

    getAllProjects() {
        return [...this.projects];
    }

    getProjectsByIndustry(industry) {
        return this.projects.filter(p => p.industry === industry);
    }

    getProjectsByStatus(status) {
        return this.projects.filter(p => p.status === status);
    }

    getStats() {
        const totalProjects = this.projects.length;
        const activeProjects = this.projects.filter(p => p.status === 'active').length;
        const totalRevenue = this.projects.reduce((sum, p) => sum + (p.revenue || 0), 0);
        const totalWorkers = this.projects.reduce((sum, p) => sum + (p.worker_count || 0), 0);

        return {
            totalProjects,
            activeProjects,
            totalRevenue,
            totalWorkers,
            averageRevenue: totalProjects > 0 ? totalRevenue / totalProjects : 0
        };
    }

    updateStats() {
        const stats = this.getStats();
        localStorage.setItem(this.stats_key, JSON.stringify(stats));
        this.dispatchEvent('stats_updated', stats);
    }

    // Industry-specific helpers
    getIndustryIcon(industry) {
        const icons = {
            manufacturing: '🏭',
            healthcare: '🏥',
            logistics: '🚛',
            enterprise: '🏢',
            retail: '🛍️',
            finance: '🏦',
            education: '🎓',
            technology: '💻'
        };
        return icons[industry] || '🏢';
    }

    getIndustryModules(industry) {
        const modules = {
            manufacturing: ['quality_control', 'chatterfix', 'safety', 'operations', 'memory'],
            healthcare: ['quality_control', 'safety', 'hr', 'linesmart', 'memory'],
            logistics: ['operations', 'safety', 'hr', 'finance', 'memory'],
            enterprise: ['quality_control', 'chatterfix', 'linesmart', 'sales', 'marketing', 'hr', 'finance', 'operations', 'safety', 'memory']
        };
        return modules[industry] || ['operations', 'memory'];
    }

    getIndustryPricing(industry, workerCount = 100) {
        const pricing = {
            manufacturing: { base: 15000, perWorker: 120 },
            healthcare: { base: 12000, perWorker: 100 },
            logistics: { base: 10000, perWorker: 90 },
            enterprise: { base: 25000, perWorker: 150 }
        };
        
        const rates = pricing[industry] || { base: 10000, perWorker: 100 };
        return rates.base + (rates.perWorker * workerCount);
    }

    // Utility methods
    generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    slugify(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/[\s_-]+/g, '-')
            .replace(/^-+|-+$/g, '');
    }

    dispatchEvent(type, data) {
        window.dispatchEvent(new CustomEvent(`fixitfred:${type}`, { detail: data }));
    }

    formatCurrency(amount) {
        if (amount >= 1000000) {
            return (amount / 1000000).toFixed(1) + 'M';
        } else if (amount >= 1000) {
            return (amount / 1000).toFixed(0) + 'K';
        }
        return amount.toString();
    }

    generateDemoProjects() {
        return [
            {
                id: 'boeing-001',
                company_name: 'Boeing Manufacturing',
                industry: 'manufacturing',
                icon: '🏭',
                status: 'active',
                worker_count: 500,
                revenue: 85000,
                modules: ['quality_control', 'chatterfix', 'safety', 'operations', 'memory'],
                created_date: '2024-01-15',
                deployment_url: 'https://boeing-manufacturing.fixitfred.ai'
            },
            {
                id: 'healthcare-002',
                company_name: 'MedTech Solutions',
                industry: 'healthcare',
                icon: '🏥',
                status: 'active',
                worker_count: 320,
                revenue: 65000,
                modules: ['quality_control', 'safety', 'hr', 'linesmart', 'memory'],
                created_date: '2024-01-20',
                deployment_url: 'https://medtech-solutions.fixitfred.ai'
            },
            {
                id: 'logistics-003',
                company_name: 'Global Logistics Corp',
                industry: 'logistics',
                icon: '🚛',
                status: 'deploying',
                worker_count: 150,
                revenue: 45000,
                modules: ['operations', 'safety', 'hr', 'finance', 'memory'],
                created_date: '2024-01-25',
                deployment_url: 'https://global-logistics-corp.fixitfred.ai'
            }
        ];
    }

    // API Integration methods
    async syncWithAPI() {
        try {
            const response = await fetch('/api/professional/recent-deployments');
            if (response.ok) {
                const data = await response.json();
                // Merge with local projects
                this.mergeRemoteProjects(data.deployments || []);
            }
        } catch (error) {
            console.log('API sync not available, using local data');
        }
    }

    mergeRemoteProjects(remoteProjects) {
        // Simple merge - in production this would be more sophisticated
        remoteProjects.forEach(remote => {
            const existing = this.projects.find(p => p.id === remote.deployment_id);
            if (!existing) {
                this.addProject({
                    id: remote.deployment_id,
                    company_name: remote.company_name,
                    industry: remote.template_name.toLowerCase().includes('manufacturing') ? 'manufacturing' :
                             remote.template_name.toLowerCase().includes('healthcare') ? 'healthcare' :
                             remote.template_name.toLowerCase().includes('logistics') ? 'logistics' : 'enterprise',
                    worker_count: remote.worker_count,
                    revenue: remote.revenue,
                    modules: JSON.parse(remote.modules || '[]'),
                    status: remote.status,
                    created_date: remote.created_at?.split('T')[0] || new Date().toISOString().split('T')[0],
                    deployment_url: remote.deployment_url
                });
            }
        });
    }

    // Professional Dashboard Integration
    createQuickDeployment(templateId, companyName, workerCount) {
        const industry = templateId;
        const modules = this.getIndustryModules(industry);
        const revenue = this.getIndustryPricing(industry, workerCount);

        const project = this.addProject({
            company_name: companyName,
            industry: industry,
            worker_count: workerCount,
            revenue: revenue,
            modules: modules,
            status: 'deploying'
        });

        // Simulate deployment
        setTimeout(() => {
            this.updateProject(project.id, { status: 'active' });
        }, 3000);

        return project;
    }
}

// Initialize global project tracker
window.projectTracker = new ProjectTracker();

// Auto-sync with API every 30 seconds
setInterval(() => {
    if (window.projectTracker) {
        window.projectTracker.syncWithAPI();
    }
}, 30000);

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProjectTracker;
}