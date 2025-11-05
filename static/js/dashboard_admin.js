/**
 * Dashboard Administrativo - Inicialización de Gráficos
 * Sistema de gestión veterinaria - PetFace ID
 */

// Configuración global de Chart.js
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#6b7280';

// Paleta de colores del sistema
const chartColors = {
  primary: 'rgba(59, 130, 246, 0.8)',
  primaryBorder: 'rgb(59, 130, 246)',
  secondary: 'rgba(16, 185, 129, 0.8)',
  secondaryBorder: 'rgb(16, 185, 129)',
  success: 'rgba(16, 185, 129, 0.8)',
  successBorder: 'rgb(16, 185, 129)',
  warning: 'rgba(245, 158, 11, 0.8)',
  warningBorder: 'rgb(245, 158, 11)',
  danger: 'rgba(239, 68, 68, 0.8)',
  dangerBorder: 'rgb(239, 68, 68)',
  purple: 'rgba(139, 92, 246, 0.8)',
  purpleBorder: 'rgb(139, 92, 246)',
  emerald: 'rgba(16, 185, 129, 0.8)',
  emeraldBorder: 'rgb(16, 185, 129)',
  amber: 'rgba(245, 158, 11, 0.8)',
  amberBorder: 'rgb(245, 158, 11)',
  indigo: 'rgba(99, 102, 241, 0.8)',
  indigoBorder: 'rgb(99, 102, 241)',
  pink: 'rgba(236, 72, 153, 0.8)',
  pinkBorder: 'rgb(236, 72, 153)',
};

// Opciones comunes para todos los gráficos
const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        font: {
          size: 12,
          weight: '500'
        },
        padding: 15,
        usePointStyle: true,
        pointStyle: 'circle'
      }
    }
  }
};

/**
 * Función principal para inicializar todos los gráficos
 */
function initDashboardCharts(data) {
  // Gráfico 1: Escaneos Diarios (Línea)
  initEscaneosDiariosChart(data);
  
  // Gráfico 2: Top Razas (Barras Horizontales)
  initTopRazasChart(data);
  
  // Gráfico 3: Etapas de Vida (Pie)
  initEtapasVidaChart(data);
  
  // Gráfico 4: Estado Corporal (Doughnut)
  initEstadoCorporalChart(data);
  
  // Gráfico 5: Registros por Mes (Barras)
  initRegistrosMesChart(data);
  
  // Gráfico 6: Actividad por Hora (Línea)
  initActividadHoraChart(data);
  
  // Gráfico 7: Usuarios por Rol (Pie)
  initUsuariosRolChart(data);
  
  // Gráfico 8: Tasa de Éxito (Línea)
  initTasaExitoChart(data);
  
  // Gráfico 9: Notificaciones por Categoría (Barras)
  initNotificacionesCategoriaChart(data);
}

/**
 * Gráfico 1: Escaneos/Reconocimientos Diarios (30 días)
 */
function initEscaneosDiariosChart(data) {
  const ctx = document.getElementById('escaneosDiariosChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.escaneosDiariosLabels,
      datasets: [{
        label: 'Escaneos/Reconocimientos',
        data: data.escaneosDiariosValues,
        backgroundColor: 'rgba(16, 185, 129, 0.1)',
        borderColor: chartColors.secondaryBorder,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: chartColors.secondaryBorder,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: chartColors.secondaryBorder,
          borderWidth: 1
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

/**
 * Gráfico 2: Top 10 Razas (Barras Horizontales)
 */
function initTopRazasChart(data) {
  const ctx = document.getElementById('topRazasChart');
  if (!ctx) return;
  
  // Generar colores degradados para cada barra
  const colors = data.razasLabels.map((_, index) => {
    const hue = (index * 360) / data.razasLabels.length;
    return `hsla(${hue}, 70%, 60%, 0.8)`;
  });
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.razasLabels,
      datasets: [{
        label: 'Cantidad de Mascotas',
        data: data.razasValues,
        backgroundColor: colors,
        borderColor: colors.map(c => c.replace('0.8', '1')),
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      ...commonOptions,
      indexAxis: 'y',
      plugins: {
        ...commonOptions.plugins,
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              return `${context.parsed.x} mascotas`;
            }
          }
        }
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

/**
 * Gráfico 3: Distribución por Etapa de Vida (Pie)
 */
function initEtapasVidaChart(data) {
  const ctx = document.getElementById('etapasVidaChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: data.etapasLabels,
      datasets: [{
        data: data.etapasValues,
        backgroundColor: data.etapasColors,
        borderColor: '#ffffff',
        borderWidth: 3,
        hoverOffset: 10
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          position: 'right',
          labels: {
            padding: 20,
            font: {
              size: 13,
              weight: '500'
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.parsed / total) * 100).toFixed(1);
              return `${context.label}: ${context.parsed} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

/**
 * Gráfico 4: Estado Corporal (Doughnut)
 */
function initEstadoCorporalChart(data) {
  const ctx = document.getElementById('estadoCorporalChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.estadosLabels,
      datasets: [{
        data: data.estadosValues,
        backgroundColor: data.estadosColors,
        borderColor: '#ffffff',
        borderWidth: 3,
        hoverOffset: 10
      }]
    },
    options: {
      ...commonOptions,
      cutout: '65%',
      plugins: {
        ...commonOptions.plugins,
        legend: {
          position: 'right',
          labels: {
            padding: 20,
            font: {
              size: 13,
              weight: '500'
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.parsed / total) * 100).toFixed(1);
              return `${context.label}: ${context.parsed} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

/**
 * Gráfico 5: Registros de Mascotas por Mes (Barras)
 */
function initRegistrosMesChart(data) {
  const ctx = document.getElementById('registrosMesChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.registrosMesLabels,
      datasets: [{
        label: 'Nuevas Mascotas',
        data: data.registrosMesValues,
        backgroundColor: chartColors.primary,
        borderColor: chartColors.primaryBorder,
        borderWidth: 1,
        borderRadius: 8
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

/**
 * Gráfico 6: Actividad por Hora del Día (Línea de área)
 */
function initActividadHoraChart(data) {
  const ctx = document.getElementById('actividadHoraChart');
  if (!ctx) return;
  
  // Crear gradiente
  const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(99, 102, 241, 0.5)');
  gradient.addColorStop(1, 'rgba(99, 102, 241, 0.05)');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.horasLabels,
      datasets: [{
        label: 'Escaneos',
        data: data.horasValues,
        backgroundColor: gradient,
        borderColor: chartColors.indigoBorder,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: chartColors.indigoBorder,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            title: function(context) {
              return `Hora: ${context[0].label}`;
            },
            label: function(context) {
              return `${context.parsed.y} escaneos`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          },
          ticks: {
            maxRotation: 45,
            minRotation: 45
          }
        }
      }
    }
  });
}

/**
 * Gráfico 7: Usuarios por Rol (Pie)
 */
function initUsuariosRolChart(data) {
  const ctx = document.getElementById('usuariosRolChart');
  if (!ctx) return;
  
  new Chart(ctx, {
    type: 'pie',
    data: {
      labels: data.rolesLabels,
      datasets: [{
        data: data.rolesValues,
        backgroundColor: data.rolesColors,
        borderColor: '#ffffff',
        borderWidth: 3,
        hoverOffset: 10
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          position: 'bottom',
          labels: {
            padding: 20,
            font: {
              size: 13,
              weight: '500'
            }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.parsed / total) * 100).toFixed(1);
              return `${context.label}: ${context.parsed} usuarios (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

/**
 * Gráfico 8: Tasa de Éxito de Reconocimientos (Línea)
 */
function initTasaExitoChart(data) {
  const ctx = document.getElementById('tasaExitoChart');
  if (!ctx) return;
  
  // Crear gradiente
  const gradient = ctx.getContext('2d').createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, 'rgba(16, 185, 129, 0.3)');
  gradient.addColorStop(1, 'rgba(16, 185, 129, 0.05)');
  
  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.tasaExitoLabels,
      datasets: [{
        label: 'Tasa de Éxito (%)',
        data: data.tasaExitoValues,
        backgroundColor: gradient,
        borderColor: chartColors.successBorder,
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: chartColors.successBorder,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12,
          callbacks: {
            label: function(context) {
              return `Tasa de éxito: ${context.parsed.y.toFixed(1)}%`;
            }
          }
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: function(value) {
              return value + '%';
            }
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

/**
 * Gráfico 9: Notificaciones por Categoría (Barras)
 */
function initNotificacionesCategoriaChart(data) {
  const ctx = document.getElementById('notificacionesCategoriaChart');
  if (!ctx) return;
  
  // Generar colores para cada categoría
  const colors = [
    chartColors.primary,
    chartColors.secondary,
    chartColors.purple,
    chartColors.amber,
    chartColors.danger,
    chartColors.emerald,
    chartColors.indigo,
    chartColors.pink,
    chartColors.warning
  ];
  
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.notifCatLabels,
      datasets: [{
        label: 'Cantidad',
        data: data.notifCatValues,
        backgroundColor: colors.slice(0, data.notifCatLabels.length),
        borderColor: colors.slice(0, data.notifCatLabels.length).map(c => c.replace('0.8', '1')),
        borderWidth: 1,
        borderRadius: 8
      }]
    },
    options: {
      ...commonOptions,
      plugins: {
        ...commonOptions.plugins,
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          padding: 12
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        x: {
          grid: {
            display: false
          }
        }
      }
    }
  });
}

// Actualizar fecha actual en tiempo real
setInterval(() => {
  const dateElement = document.getElementById('current-date');
  if (dateElement) {
    const now = new Date();
    const options = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    dateElement.textContent = now.toLocaleString('es-ES', options);
  }
}, 60000); // Actualizar cada minuto
