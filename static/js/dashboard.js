// Dashboard JavaScript functionality

document.addEventListener("DOMContentLoaded", function () {
  // Initialize dashboard components
  initializeCounters();
  initializeTooltips();

  // Auto-refresh data every 5 minutes for real-time stats
  if (window.location.pathname.includes("dashboard")) {
    setInterval(refreshStats, 300000); // 5 minutes
  }
});

function initializeCounters() {
  // Animated counters for statistics
  const counters = document.querySelectorAll(".counter");

  counters.forEach((counter) => {
    const target = parseInt(counter.textContent);
    const increment = target / 100;
    let current = 0;

    const updateCounter = () => {
      if (current < target) {
        current += increment;
        counter.textContent = Math.ceil(current);
        requestAnimationFrame(updateCounter);
      } else {
        counter.textContent = target;
      }
    };

    // Start animation when element is visible
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          updateCounter();
          observer.unobserve(entry.target);
        }
      });
    });

    observer.observe(counter);
  });
}

function initializeTooltips() {
  // Simple tooltip functionality
  const tooltipTriggers = document.querySelectorAll("[data-tooltip]");

  tooltipTriggers.forEach((trigger) => {
    trigger.addEventListener("mouseenter", showTooltip);
    trigger.addEventListener("mouseleave", hideTooltip);
  });
}

function showTooltip(e) {
  const text = e.target.getAttribute("data-tooltip");
  const tooltip = document.createElement("div");
  tooltip.className = "tooltip";
  tooltip.textContent = text;
  tooltip.style.cssText = `
        position: absolute;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        z-index: 1000;
        pointer-events: none;
    `;

  document.body.appendChild(tooltip);

  const rect = e.target.getBoundingClientRect();
  tooltip.style.left =
    rect.left + rect.width / 2 - tooltip.offsetWidth / 2 + "px";
  tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + "px";
}

function hideTooltip() {
  const tooltip = document.querySelector(".tooltip");
  if (tooltip) {
    tooltip.remove();
  }
}

function refreshStats() {
  // Refresh dashboard statistics
  fetch(window.location.href, {
    headers: {
      "X-Requested-With": "XMLHttpRequest",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        updateStatsDisplay(data.stats);
      }
    })
    .catch((error) => {
      console.log("Stats refresh failed:", error);
    });
}

function updateStatsDisplay(stats) {
  // Update statistics in the dashboard
  Object.keys(stats).forEach((key) => {
    const element = document.querySelector(`[data-stat="${key}"]`);
    if (element) {
      element.textContent = stats[key];
    }
  });
}

// Quick actions handlers
function handleQuickAction(action) {
  switch (action) {
    case "register-pet":
      window.location.href = "/mascota/";
      break;
    case "scanner":
      window.location.href = "/scanner/";
      break;
    case "profile":
      window.location.href = "/profile/";
      break;
    case "users":
      window.location.href = "/users/";
      break;
    default:
      console.log("Unknown action:", action);
  }
}

// Chart utilities
function createLineChart(canvasId, data, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
        },
      },
    },
  };

  return new Chart(ctx, {
    type: "line",
    data: data,
    options: { ...defaultOptions, ...options },
  });
}

function createDoughnutChart(canvasId, data, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
      },
    },
  };

  return new Chart(ctx, {
    type: "doughnut",
    data: data,
    options: { ...defaultOptions, ...options },
  });
}

// Utility functions
function formatNumber(num) {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + "M";
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + "K";
  }
  return num.toString();
}

function getConfidenceClass(confidence) {
  if (confidence >= 0.8) return "confidence-high";
  if (confidence >= 0.6) return "confidence-medium";
  return "confidence-low";
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function formatTime(dateString) {
  const date = new Date(dateString);
  return date.toLocaleTimeString("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

// Export functions for use in templates
window.Dashboard = {
  handleQuickAction,
  createLineChart,
  createDoughnutChart,
  formatNumber,
  getConfidenceClass,
  formatDate,
  formatTime,
};
