/* ============================================================
   KKR 2026 SEASON - FRONTEND CLIENT
   Communicates with backend API at http://https://kkr-fan-hub.onrender.com:5000/api
   Resiliently falls back to local data if backend is offline.
============================================================ */

// Environment Detection & Configuration
const isLocalhost =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1";

const currentEnv = isLocalhost ? "development" : "production";

const ENV = {
  development: {
    FRONTEND_URL: "http://localhost:3000",
    API_BASE_URL: "http://localhost:5000/api",
    WS_BASE_URL: "ws://localhost:5000"
  },

  production: {
    FRONTEND_URL: window.location.origin,
    API_BASE_URL: "https://kkr-fan-hub.onrender.com/api",
    WS_BASE_URL: "wss://kkr-fan-hub.onrender.com"
  }
};

const FRONTEND_URL = window.FRONTEND_URL || ENV[currentEnv].FRONTEND_URL;
const API_URL = window.API_BASE_URL || ENV[currentEnv].API_BASE_URL;
const WS_BASE_URL = window.WS_BASE_URL || ENV[currentEnv].WS_BASE_URL;

// WebSocket Connection Managers for Cheers Wall and MVP Poll
function connectPollWebSocket() {
  const wsUrl = `${WS_BASE_URL}/ws/poll`;
  console.log(`Connecting to Poll WebSocket at: ${wsUrl}`);
  
  const ws = new WebSocket(wsUrl);
  let pingInterval;
  
  ws.onopen = () => {
    console.log("WebSocket success: Poll WebSocket connection established.");
    pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 30000);
  };
  
  ws.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.event === "poll_update") {
        pollVotes = payload.data.votes;
        pollLabels = payload.data.labels;
        const pollOptionsContainer = document.getElementById("pollOptions");
        const pollTotal = document.getElementById("pollTotal");
        if (pollOptionsContainer && pollTotal) {
          renderPollOptions(pollLabels, pollOptionsContainer, pollTotal);
        }
      }
    } catch (err) {
      // Quietly ignore parsing anomalies or ping/pong frames
    }
  };
  
  ws.onclose = () => {
    console.log("WebSocket failure: Poll WebSocket connection closed/failed. Reconnecting in 5 seconds...");
    clearInterval(pingInterval);
    setTimeout(connectPollWebSocket, 5000);
  };
  
  ws.onerror = (err) => {
    console.error("WebSocket failure: Poll WebSocket error: ", err);
    ws.close();
  };
}

function connectCheersWebSocket(onUpdate) {
  const wsUrl = `${WS_BASE_URL}/ws/cheers`;
  console.log(`Connecting to Cheers WebSocket at: ${wsUrl}`);
  
  const ws = new WebSocket(wsUrl);
  let pingInterval;
  
  ws.onopen = () => {
    console.log("WebSocket success: Cheers WebSocket connection established.");
    pingInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send("ping");
      }
    }, 30000);
  };
  
  ws.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.event === "cheer_update") {
        if (typeof onUpdate === "function") {
          onUpdate(payload.data);
        }
      }
    } catch (err) {
      // Quietly ignore parsing anomalies or ping/pong frames
    }
  };
  
  ws.onclose = () => {
    console.log("WebSocket failure: Cheers WebSocket connection closed/failed. Reconnecting in 5 seconds...");
    clearInterval(pingInterval);
    setTimeout(() => connectCheersWebSocket(onUpdate), 5000);
  };
  
  ws.onerror = (err) => {
    console.error("WebSocket failure: Cheers WebSocket error: ", err);
    ws.close();
  };
}
// Native Toast Alert Notifications Utility
function showToast(message, type = 'info') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  let icon = 'ℹ️';
  if (type === 'success') icon = '✅';
  else if (type === 'error') icon = '❌';
  else if (type === 'warning') icon = '⚠️';
  
  toast.innerHTML = `
    <span style="font-size: 1.25rem;">${icon}</span>
    <span class="toast-message">${message}</span>
    <button class="toast-close">&times;</button>
  `;
  
  container.appendChild(toast);
  
  // Animation delay
  setTimeout(() => toast.classList.add('visible'), 10);
  
  const closeToast = () => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 300);
  };
  
  toast.querySelector('.toast-close').addEventListener('click', closeToast);
  setTimeout(closeToast, 5000);
}

// Offline UI Indicator Banner
function showOfflineBanner() {
  if (!document.getElementById('offline-banner')) {
    const banner = document.createElement('div');
    banner.id = 'offline-banner';
    banner.innerHTML = `⚠️ Running in Offline Mode (Offline fallback database enabled)`;
    document.body.insertBefore(banner, document.body.firstChild);
  }
}

// Shimmer Loading Skeletons Renderer
function showSkeletons() {
  const scheduleGrid = document.querySelector(".schedule-grid");
  const newsGrid = document.querySelector(".news-grid");
  const squadGrid = document.querySelector(".squad-grid");
  const legendsGrid = document.querySelector(".legends-grid");

  if (scheduleGrid) {
    scheduleGrid.innerHTML = Array(3).fill(0).map(() => `
      <div class="skeleton-card" style="height: 180px;"></div>
    `).join('');
  }
  if (newsGrid) {
    newsGrid.innerHTML = Array(3).fill(0).map(() => `
      <div class="skeleton-card" style="height: 280px;"></div>
    `).join('');
  }
  if (squadGrid) {
    squadGrid.innerHTML = Array(4).fill(0).map(() => `
      <div class="skeleton-card" style="height: 380px;"></div>
    `).join('');
  }
  if (legendsGrid) {
    legendsGrid.innerHTML = Array(3).fill(0).map(() => `
      <div class="skeleton-card" style="height: 300px;"></div>
    `).join('');
  }
}

const FALLBACK_DATA = {
  players: [
    {
        "name": "Manish Pandey",
        "jersey": 9,
        "role": "Batter",
        "country": "India",
        "bio": "A name that has lived rent-free in our minds but could not have a similar impact in the Indian national side. Not taking any dig at this exceptional batter, but he certainly could not reach the limits that everyone...",
        "stats": [
            {
                "k": "Matches",
                "v": "6"
            },
            {
                "k": "Runs",
                "v": "70"
            },
            {
                "k": "S/R",
                "v": "142.86"
            }
        ],
        "image": "images/manish-pandey.jpg"
    },
    {
        "name": "Ajinkya Rahane",
        "jersey": 3,
        "role": "Batter",
        "country": "India",
        "bio": "Ajinkya Rahane, a right-handed top-order batter from Mumbai is a perfect combination of talent, consistency and aggression. He made his first-class debut for Mumbai in 2007. In only his second Ranji season, he...",
        "stats": [
            {
                "k": "Matches",
                "v": "14"
            },
            {
                "k": "Runs",
                "v": "335"
            },
            {
                "k": "S/R",
                "v": "135.08"
            }
        ],
        "image": "images/ajinkya-rahane.jpg"
    },
    {
        "name": "Angkrish Raghuvanshi",
        "jersey": 18,
        "role": "Wicketkeeper",
        "country": "India",
        "bio": "Angkrish Raghuvanshi is a right-handed batter who bowls left-arm orthodox spin and he represents Mumbai in the Indian domestic circuit. Angkrish Raghuvanshi was born on June 5, 2005 in Delhi.",
        "stats": [
            {
                "k": "Matches",
                "v": "13"
            },
            {
                "k": "Runs",
                "v": "422"
            },
            {
                "k": "Catches",
                "v": "5"
            }
        ],
        "image": "images/angkrish-raghuvanshi.jpg"
    },
    {
        "name": "Finn Allen",
        "jersey": 16,
        "role": "Batter",
        "country": "New Zealand",
        "bio": "New Zealand have produced one of the most destructive openers in Brendon McCullum who terrorised the bowlers throughout his career. Talking about explosive Kiwi openers, Finnley Hugh Allen is...",
        "stats": [
            {
                "k": "Matches",
                "v": "11"
            },
            {
                "k": "Runs",
                "v": "349"
            },
            {
                "k": "S/R",
                "v": "214.11"
            }
        ],
        "image": "images/finn-allen.jpg"
    },
    {
        "name": "Rinku Singh",
        "jersey": 35,
        "role": "Batter",
        "country": "India",
        "bio": "Rinku Singh, a left-handed batter from Aligarh, has emerged as a promising talent in Indian cricket, captivating fans with his aggressive batting style and consistent performances. His journey from the...",
        "stats": [
            {
                "k": "Matches",
                "v": "14"
            },
            {
                "k": "Runs",
                "v": "295"
            },
            {
                "k": "S/R",
                "v": "148.99"
            }
        ],
        "image": "images/rinku-singh.jpg"
    },
    {
        "name": "Rovman Powell",
        "jersey": 52,
        "role": "Batter",
        "country": "Jamaica",
        "bio": "Rovman Powell is a Jamaican cricketer. He is primarily a middle-order batter and an occasional medium-pace bowler. He has been representing West Indies in ODIs since 2016 but it took him close to five years to secure...",
        "stats": [
            {
                "k": "Matches",
                "v": "11"
            },
            {
                "k": "Runs",
                "v": "190"
            },
            {
                "k": "S/R",
                "v": "134.75"
            }
        ],
        "image": "images/rovman-powell.jpg"
    },
    {
        "name": "Ramandeep Singh",
        "jersey": 19,
        "role": "Batter",
        "country": "India",
        "bio": "Ramandeep Singh, born on April 13, 1997, is an Indian cricketer known for his right-handed batting and part-time medium pace. Hailing from Punjab, Ramandeep's journey in cricket exemplifies determination and...",
        "stats": [
            {
                "k": "Matches",
                "v": "8"
            },
            {
                "k": "Runs",
                "v": "82"
            },
            {
                "k": "S/R",
                "v": "120.59"
            }
        ],
        "image": "images/ramandeep-singh.jpg"
    },
    {
        "name": "Tim Seifert",
        "jersey": 43,
        "role": "Wicketkeeper",
        "country": "New Zealand",
        "bio": "Explosive with the bat and sharp behind the stumps, Tim Seifert has built a reputation as one of New Zealand's most dynamic wicketkeeper-batters in white-ball cricket. Born in Whanganui in 1994, the right-hander...",
        "stats": [
            {
                "k": "Matches",
                "v": "3"
            },
            {
                "k": "Runs",
                "v": "19"
            },
            {
                "k": "Catches",
                "v": "2"
            }
        ],
        "image": "images/tim-seifert.jpg"
    },
    {
        "name": "Tejasvi Singh",
        "jersey": 12,
        "role": "Wicketkeeper",
        "country": "India",
        "bio": "A fearless six-hitter with a flair for dramatic cameos, Tejasvi Singh Dahiya has quickly risen through Delhi's cricketing ranks with his explosive batting and sharp wicketkeeping. A self-confessed fan of Virender...",
        "stats": [
            {
                "k": "Matches",
                "v": "2"
            },
            {
                "k": "Runs",
                "v": "12"
            },
            {
                "k": "Catches",
                "v": "1"
            }
        ],
        "image": "images/tejasvi-singh.jpg"
    },
    {
        "name": "Sunil Narine",
        "jersey": 74,
        "role": "All-Rounder",
        "country": "West Indies",
        "bio": "With multiple limited-overs tournaments on the rise across the globe, franchises are in search of mystery spinners who can bowl in the Powerplay as well as provide breakthroughs once the field restrictions are eased.",
        "stats": [
            {
                "k": "Matches",
                "v": "13"
            },
            {
                "k": "Runs",
                "v": "40"
            },
            {
                "k": "Wickets",
                "v": "15"
            }
        ],
        "image": "images/sunil-narine.jpg"
    },
    {
        "name": "Cameron Green",
        "jersey": 42,
        "role": "All-Rounder",
        "country": "Australia",
        "bio": "Cameron Green is a highly promising and versatile cricketer who hails from Australia. He is often regarded as the next best thing in Australian cricket and his unique ability to excel both as a right-handed batter...",
        "stats": [
            {
                "k": "Matches",
                "v": "14"
            },
            {
                "k": "Runs",
                "v": "322"
            },
            {
                "k": "Wickets",
                "v": "7"
            }
        ],
        "image": "images/cameron-green.jpg"
    },
    {
        "name": "Anukul Roy",
        "jersey": 6,
        "role": "All-Rounder",
        "country": "India",
        "bio": "Anukul Roy is an emerging star in Indian cricket, renowned for his impactful lower-order batting and skillful left-arm orthodox spin. He first gained attention during the 2018 ICC Under-19 Cricket World Cup, where...",
        "stats": [
            {
                "k": "Matches",
                "v": "14"
            },
            {
                "k": "Runs",
                "v": "52"
            },
            {
                "k": "Wickets",
                "v": "9"
            }
        ],
        "image": "images/anukul-roy.jpg"
    },
    {
        "name": "Kartik Tyagi",
        "jersey": 9,
        "role": "Bowler",
        "country": "India",
        "bio": "A young talent with a promising future, Kartik Tyagi, born 8th of November 2000, is a right-arm fast-medium bowler known for his ability to swing the ball both ways. A kid from Hapur, a city in Uttar Pradesh, emerged in the...",
        "stats": [
            {
                "k": "Matches",
                "v": "14"
            },
            {
                "k": "Wickets",
                "v": "18"
            },
            {
                "k": "Econ",
                "v": "9.76"
            }
        ],
        "image": "images/kartik-tyagi.jpg"
    },
    {
        "name": "Varun Chakaravarthy",
        "jersey": 29,
        "role": "Bowler",
        "country": "India",
        "bio": "'Mystery' is a word that always brings a sense of excitement with it. In cricket too, mystery bowlers over the years have tormented batters with a sense of anticipation and thrill among the cricketing fraternity.",
        "stats": [
            {
                "k": "Matches",
                "v": "11"
            },
            {
                "k": "Wickets",
                "v": "11"
            },
            {
                "k": "Econ",
                "v": "8.78"
            }
        ],
        "image": "images/varun-chakaravarthy.jpg"
    },
    {
        "name": "Vaibhav Arora",
        "jersey": 22,
        "role": "Bowler",
        "country": "India",
        "bio": "Vaibhav Arora is a right-arm pace bowler from India. Born on 14th December 1997, the Haryana-born cricketer began his professional career when he made his first-class debut for Himachal Pradesh against...",
        "stats": [
            {
                "k": "Matches",
                "v": "11"
            },
            {
                "k": "Wickets",
                "v": "11"
            },
            {
                "k": "Econ",
                "v": "10.26"
            }
        ],
        "image": "images/vaibhav-arora.jpg"
    },
    {
        "name": "Saurabh Dubey",
        "jersey": 32,
        "role": "Bowler",
        "country": "India",
        "bio": "A developing bowler working his way into the squad, adding depth and rotational options to the franchise's fast bowling reserves.",
        "stats": [
            {
                "k": "Matches",
                "v": "4"
            },
            {
                "k": "Wickets",
                "v": "5"
            },
            {
                "k": "Econ",
                "v": "8.26"
            }
        ],
        "image": "images/saurabh-dubey.jpg"
    },
    {
        "name": "Blessing Muzarabani",
        "jersey": 85,
        "role": "Bowler",
        "country": "Zimbabwe",
        "bio": "A tall right-arm fast bowler offering menacing bounce and pace. He has been a consistent wicket-taker and brings an aggressive edge to the bowling lineup.",
        "stats": [
            {
                "k": "Matches",
                "v": "2"
            },
            {
                "k": "Wickets",
                "v": "4"
            },
            {
                "k": "Econ",
                "v": "10.71"
            }
        ],
        "image": "images/blessing-muzarabani.jpg"
    },
    {
        "name": "Navdeep Saini",
        "jersey": 96,
        "role": "Bowler",
        "country": "India",
        "bio": "Son of a driver hailing from Haryana, Navdeep is a dedicated right-arm pacer who represents Delhi in the domestic circuit and has been a valuable player for them in recent years. Saini made headlines in the 2017...",
        "stats": [
            {
                "k": "Matches",
                "v": "2"
            },
            {
                "k": "Wickets",
                "v": "0"
            },
            {
                "k": "Econ",
                "v": "12.33"
            }
        ],
        "image": "images/navdeep-saini.jpg"
    },
    {
        "name": "Rahul Tripathi",
        "jersey": 52,
        "role": "Batter",
        "country": "India",
        "bio": "Rahul Tripathi is a flamboyant right-handed batter with almost all the shots in the book one can ask for. His ability to keep the game moving and be busy at the crease is one aspect that makes him stand out.",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Runs",
                "v": "0"
            },
            {
                "k": "S/R",
                "v": "0"
            }
        ],
        "image": "images/rahul-tripathi.jpg"
    },
    {
        "name": "Sarthak Ranjan",
        "jersey": 10,
        "role": "Batter",
        "country": "India",
        "bio": "A powerful top-order batter with a fearless approach, Sarthak Ranjan has carved a path through persistence and late recognition in Indian domestic cricket. Known for his clean striking and attacking intent, the Delhi...",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Runs",
                "v": "0"
            },
            {
                "k": "S/R",
                "v": "0"
            }
        ],
        "image": "images/sarthak-ranjan.jpg"
    },
    {
        "name": "Rachin Ravindra",
        "jersey": 8,
        "role": "All-Rounder",
        "country": "New Zealand",
        "bio": "Rachin Ravindra is an exciting cricketer from New Zealand who quickly made a name for himself on the international stage. His journey from the streets of Wellington to a sensational World Cup debut is a...",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Runs",
                "v": "0"
            },
            {
                "k": "Wickets",
                "v": "0"
            }
        ],
        "image": "images/rachin-ravindra.jpg"
    },
    {
        "name": "Daksh Kamra",
        "jersey": 33,
        "role": "All-Rounder",
        "country": "India",
        "bio": "Mystery spinners have increasingly become valuable assets in the T20 era, and Daksh Kamra is one of the latest young talents attempting to make a mark with his craft. Hailing from Hisar in Haryana, Kamra is...",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Runs",
                "v": "0"
            },
            {
                "k": "Wickets",
                "v": "0"
            }
        ],
        "image": "images/daksh-kamra.jpg"
    },
    {
        "name": "Luvnith Sisodia",
        "jersey": 14,
        "role": "Wicketkeeper",
        "country": "India",
        "bio": "Luvnith Sisodia, born and brought up in Bangalore, Karnataka, is a dynamic young cricketer making waves with his aggressive left-handed batting and exceptional wicketkeeping skills. His remarkable talent has drawn...",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Runs",
                "v": "0"
            },
            {
                "k": "Catches",
                "v": "0"
            }
        ],
        "image": "images/luvnith-sisodia.jpg"
    },
    {
        "name": "Prashant Solanki",
        "jersey": 44,
        "role": "Bowler",
        "country": "India",
        "bio": "Prashant Solanki is a right-arm leg-break bowler hailing from Mumbai. He was born on February 22, 2000 in Jodhpur, Rajasthan. He is a state-level cricket player representing the Mumbai team in state-level cricket...",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Wickets",
                "v": "0"
            },
            {
                "k": "Econ",
                "v": "0.00"
            }
        ],
        "image": "images/prashant-solanki.jpg"
    },
    {
        "name": "Umran Malik",
        "jersey": 24,
        "role": "Bowler",
        "country": "India",
        "bio": "Umran Malik is a remarkable right-arm fast bowler hailing from Jammu, India, celebrated for his incredible speed on the cricket field. Rising through the competitive cricket circuits of Jammu and Kashmir...",
        "stats": [
            {
                "k": "Matches",
                "v": "0"
            },
            {
                "k": "Wickets",
                "v": "0"
            },
            {
                "k": "Econ",
                "v": "0.00"
            }
        ],
        "image": "images/umran-malik.jpg"
    }
],
  masterStats: {
    "Sunil Narine": [
        {
            "k": "Matches",
            "v": "13"
        },
        {
            "k": "Runs",
            "v": "40"
        },
        {
            "k": "Wickets",
            "v": "15"
        },
        {
            "k": "S/R",
            "v": "125.00"
        }
    ],
    "Rahul Tripathi": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Runs",
            "v": "0"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "0.00"
        }
    ],
    "Tim Seifert": [
        {
            "k": "Matches",
            "v": "3"
        },
        {
            "k": "Runs",
            "v": "19"
        },
        {
            "k": "Stumpings",
            "v": "1"
        },
        {
            "k": "Catches",
            "v": "2"
        }
    ],
    "Navdeep Saini": [
        {
            "k": "Matches",
            "v": "2"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "Best",
            "v": "0"
        },
        {
            "k": "Econ",
            "v": "12.33"
        }
    ],
    "Rinku Singh": [
        {
            "k": "Matches",
            "v": "14"
        },
        {
            "k": "Runs",
            "v": "295"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "148.99"
        }
    ],
    "Rovman Powell": [
        {
            "k": "Matches",
            "v": "11"
        },
        {
            "k": "Runs",
            "v": "190"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "134.75"
        }
    ],
    "Sarthak Ranjan": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Runs",
            "v": "0"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "0.00"
        }
    ],
    "Finn Allen": [
        {
            "k": "Matches",
            "v": "11"
        },
        {
            "k": "Runs",
            "v": "349"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "214.11"
        }
    ],
    "Rachin Ravindra": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Runs",
            "v": "0"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "0.00"
        }
    ],
    "Cameron Green": [
        {
            "k": "Matches",
            "v": "14"
        },
        {
            "k": "Runs",
            "v": "322"
        },
        {
            "k": "Wickets",
            "v": "7"
        },
        {
            "k": "S/R",
            "v": "145.70"
        }
    ],
    "Ramandeep Singh": [
        {
            "k": "Matches",
            "v": "8"
        },
        {
            "k": "Runs",
            "v": "82"
        },
        {
            "k": "Wickets",
            "v": "1"
        },
        {
            "k": "S/R",
            "v": "120.59"
        }
    ],
    "Anukul Roy": [
        {
            "k": "Matches",
            "v": "14"
        },
        {
            "k": "Runs",
            "v": "52"
        },
        {
            "k": "Wickets",
            "v": "9"
        },
        {
            "k": "S/R",
            "v": "133.33"
        }
    ],
    "Varun Chakaravarthy": [
        {
            "k": "Matches",
            "v": "11"
        },
        {
            "k": "Wickets",
            "v": "11"
        },
        {
            "k": "Best",
            "v": "-"
        },
        {
            "k": "Econ",
            "v": "8.78"
        }
    ],
    "Kartik Tyagi": [
        {
            "k": "Matches",
            "v": "14"
        },
        {
            "k": "Wickets",
            "v": "18"
        },
        {
            "k": "Best",
            "v": "-"
        },
        {
            "k": "Econ",
            "v": "9.76"
        }
    ],
    "Blessing Muzarabani": [
        {
            "k": "Matches",
            "v": "2"
        },
        {
            "k": "Wickets",
            "v": "4"
        },
        {
            "k": "Best",
            "v": "-"
        },
        {
            "k": "Econ",
            "v": "10.71"
        }
    ],
    "Luvnith Sisodia": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Runs",
            "v": "0"
        },
        {
            "k": "Stumpings",
            "v": "0"
        },
        {
            "k": "Catches",
            "v": "0"
        }
    ],
    "Prashant Solanki": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "Best",
            "v": "0"
        },
        {
            "k": "Econ",
            "v": "0.00"
        }
    ],
    "Saurabh Dubey": [
        {
            "k": "Matches",
            "v": "4"
        },
        {
            "k": "Wickets",
            "v": "5"
        },
        {
            "k": "Best",
            "v": "-"
        },
        {
            "k": "Econ",
            "v": "8.26"
        }
    ],
    "Vaibhav Arora": [
        {
            "k": "Matches",
            "v": "11"
        },
        {
            "k": "Wickets",
            "v": "11"
        },
        {
            "k": "Best",
            "v": "-"
        },
        {
            "k": "Econ",
            "v": "10.26"
        }
    ],
    "Umran Malik": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "Best",
            "v": "0"
        },
        {
            "k": "Econ",
            "v": "0.00"
        }
    ],
    "Angkrish Raghuvanshi": [
        {
            "k": "Matches",
            "v": "13"
        },
        {
            "k": "Runs",
            "v": "422"
        },
        {
            "k": "Stumpings",
            "v": "1"
        },
        {
            "k": "Catches",
            "v": "5"
        }
    ],
    "Tejasvi Singh": [
        {
            "k": "Matches",
            "v": "2"
        },
        {
            "k": "Runs",
            "v": "12"
        },
        {
            "k": "Stumpings",
            "v": "0"
        },
        {
            "k": "Catches",
            "v": "1"
        }
    ],
    "Daksh Kamra": [
        {
            "k": "Matches",
            "v": "0"
        },
        {
            "k": "Runs",
            "v": "0"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "S/R",
            "v": "0.00"
        }
    ],
    "Ajinkya Rahane": [
        {
            "k": "Matches",
            "v": "14"
        },
        {
            "k": "Runs",
            "v": "335"
        },
        {
            "k": "Avg",
            "v": "-"
        },
        {
            "k": "S/R",
            "v": "135.08"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "Econ",
            "v": "0.00"
        },
        {
            "k": "Catches",
            "v": "0"
        }
    ],
    "Manish Pandey": [
        {
            "k": "Matches",
            "v": "6"
        },
        {
            "k": "Runs",
            "v": "70"
        },
        {
            "k": "Avg",
            "v": "-"
        },
        {
            "k": "S/R",
            "v": "142.86"
        },
        {
            "k": "Wickets",
            "v": "0"
        },
        {
            "k": "Econ",
            "v": "0.00"
        },
        {
            "k": "Catches",
            "v": "0"
        }
    ]
},
  matches: [
    { date: "29 MAR 2026", opp: "Mumbai Indians", venue: "Wankhede Stadium, Mumbai", vs: "MI", status: "lost", desc: "MI won by 6 wickets", theme: "background:#001f5b;color:#99cfff;border-color:#3a6abf" },
    { date: "02 APR 2026", opp: "Sunrisers Hyderabad", venue: "Eden Gardens, Kolkata", vs: "SRH", status: "won", desc: "KKR won by 4 wickets", theme: "background:#d71920;color:#fff;border-color:#d71920" },
    { date: "06 APR 2026", opp: "Punjab Kings", venue: "Eden Gardens, Kolkata", vs: "PBKS", status: "won", desc: "KKR won by 18 runs", theme: "background:#e31937;color:#fff;border-color:#ffd700" },
    { date: "09 APR 2026", opp: "Lucknow Super Giants", venue: "Eden Gardens, Kolkata", vs: "LSG", status: "lost", desc: "LSG won by 5 wickets", theme: "background:#1a5276;color:#a3d5f7;border-color:#4ca6d9" },
    { date: "14 APR 2026", opp: "Royal Challengers Bengaluru", venue: "M. Chinnaswamy Stadium, Bengaluru", vs: "RCB", status: "won", desc: "KKR won by 5 wickets", theme: "background:#c8102e;color:#fff;border-color:#c8102e" },
    { date: "18 APR 2026", opp: "Delhi Capitals", venue: "Arun Jaitley Stadium, Delhi", vs: "DC", status: "won", desc: "KKR won by 22 runs", theme: "background:#004c97;color:#ffd700;border-color:#ffd700" },
    { date: "22 APR 2026", opp: "Rajasthan Royals", venue: "Eden Gardens, Kolkata", vs: "RR", status: "noresult", desc: "Match washed out due to rain", theme: "background:#ea1b86;color:#fff;border-color:#004b87" },
    { date: "27 APR 2026", opp: "Chennai Super Kings", venue: "MA Chidambaram Stadium, Chennai", vs: "CSK", status: "lost", desc: "CSK won by 7 wickets", theme: "background:#004c97;color:#ffd700;border-color:#ffd700" },
    { date: "30 APR 2026", opp: "Gujarat Titans", venue: "Narendra Modi Stadium, Ahmedabad", vs: "GT", status: "lost", desc: "GT won by 12 runs", theme: "background:#0b1d3a;color:#d4af37;border-color:#d4af37" },
    { date: "04 MAY 2026", opp: "Sunrisers Hyderabad", venue: "Rajiv Gandhi Stadium, Hyderabad", vs: "SRH", status: "won", desc: "KKR won by 7 wickets", theme: "background:#d71920;color:#fff;border-color:#d71920" },
    { date: "08 MAY 2026", opp: "Royal Challengers Bengaluru", venue: "Eden Gardens, Kolkata", vs: "RCB", status: "won", desc: "KKR won by 3 wickets", theme: "background:#c8102e;color:#fff;border-color:#c8102e" },
    { date: "13 MAY 2026", opp: "Chennai Super Kings", venue: "Eden Gardens, Kolkata", vs: "CSK", status: "lost", desc: "CSK won by 6 wickets", theme: "background:#004c97;color:#ffd700;border-color:#ffd700" },
    { date: "17 MAY 2026", opp: "Mumbai Indians", venue: "Eden Gardens, Kolkata", vs: "MI", status: "lost", desc: "MI won by 4 runs", theme: "background:#001f5b;color:#99cfff;border-color:#3a6abf" },
    { date: "24 MAY 2026", opp: "Delhi Capitals", venue: "Eden Gardens, Kolkata", vs: "DC", status: "lost", desc: "DC won by 40 runs", theme: "background:#004c97;color:#ffd700;border-color:#ffd700" }
  ],
  newsArticles: [
    {
      date: "MAY 24, 2026",
      cat: "Match Report",
      headline: "Heartbreak at Eden: KKR Miss Out on Playoffs After Defeat to DC",
      snippet: "A devastating 40-run loss to the Delhi Capitals in their final league game sealed KKR's fate, finishing 7th in the points table with 13 points after a fighting season.",
      link: "#"
    },
    {
      date: "MAY 18, 2026",
      cat: "Squad Update",
      headline: "Rinku Singh Officially Appointed Vice-Captain for the Future",
      snippet: "KKR management confirmed that Rinku Singh will take over as a key pillar in the leadership team, marking his rise from a breakout finisher to the squad's core leader.",
      link: "#"
    },
    {
      date: "MAY 09, 2026",
      cat: "Interview",
      headline: "Sunil Narine: 'Eden Gardens Has Always Felt Like My Home'",
      snippet: "Completing his 14th year with the Knight Riders, Sunil Narine opened up about his journey, expressing deep appreciation for the fans who supported him since 2012.",
      link: "#"
    },
    {
      date: "MAY 05, 2026",
      cat: "Match Report",
      headline: "Venkatesh Iyer's Brilliant 62 Steers KKR to Victory in Hyderabad",
      snippet: "Iyer's explosive half-century and a combined bowling effort from spinners Varun and Narine powered KKR to a clinical 7-wicket victory against SRH.",
      link: "#"
    },
    {
      date: "APRIL 23, 2026",
      cat: "Update",
      headline: "Rain Spoils Play: KKR vs RR Match Abandoned at Eden Gardens",
      snippet: "Unseasonal showers washed out the highly anticipated match between KKR and RR. Both teams shared one point, impacting the tight mid-table playoff race.",
      link: "#"
    },
    {
      date: "MARCH 30, 2026",
      cat: "Analysis",
      headline: "Skipper Ajinkya Rahane Demands Better Powerplay Execution",
      snippet: "Following a 6-wicket loss to MI in the tournament opener, captain Ajinkya Rahane urged the team to tighten up bowling lines and build better opening partnerships.",
      link: "#"
    }
  ],
  quizQuestions: [
    {
        "q": "Who faced the very first delivery in IPL history during the inaugural 2008 match?",
        "opts": [
            "Brendon McCullum",
            "Sourav Ganguly",
            "Sachin Tendulkar",
            "Virender Sehwag"
        ],
        "ans": 1,
        "exp": "Correct! Sourav Ganguly faced the first-ever IPL ball on April 18, 2008, bowled by RCB's Praveen Kumar."
    },
    {
        "q": "In which years has Kolkata Knight Riders won the IPL Championship?",
        "opts": [
            "2010, 2012, 2018",
            "2012, 2014, 2021",
            "2012, 2014, 2024",
            "2008, 2014, 2024"
        ],
        "ans": 2,
        "exp": "Awesome! KKR lifted the trophy in 2012, 2014 (both under Gautam Gambhir), and in 2024."
    },
    {
        "q": "What is the name of KKR's official anthem?",
        "opts": [
            "Ami KKR",
            "Korbo Lorbo Jeetbo Re",
            "Purple Army March",
            "Roar of the Knights"
        ],
        "ans": 1,
        "exp": "Korbo Lorbo Jeetbo Re (We will do, we will fight, we will win) has been the iconic anthem since 2008!"
    },
    {
        "q": "KKR holds the record for the longest winning streak by any Indian T20 team. How many consecutive matches did they win in 2014?",
        "opts": [
            "10 Matches",
            "12 Matches",
            "14 Matches",
            "16 Matches"
        ],
        "ans": 2,
        "exp": "Unbelievable but true! KKR won 14 matches in a row (9 in the IPL and 5 in the Champions League T20) during their golden run in 2014."
    },
    {
        "q": "Who scored a legendary 158* in the very first match of the IPL in 2008?",
        "opts": [
            "Sourav Ganguly",
            "Chris Gayle",
            "Jacques Kallis",
            "Brendon McCullum"
        ],
        "ans": 3,
        "exp": "Brendon McCullum smashed 158 not out off just 73 balls, setting the IPL on fire on night one."
    },
    {
        "q": "Which KKR legend hit 5 consecutive sixes in the final over against Gujarat Titans in 2023 to win an impossible match?",
        "opts": [
            "Andre Russell",
            "Rinku Singh",
            "Sunil Narine",
            "Venkatesh Iyer"
        ],
        "ans": 1,
        "exp": "Rinku Singh did the unthinkable, hitting 5 sixes off Yash Dayal when KKR needed 28 runs off 5 balls!"
    },
    {
        "q": "Who is the all-time leading wicket-taker for Kolkata Knight Riders?",
        "opts": [
            "Andre Russell",
            "Piyush Chawla",
            "Sunil Narine",
            "Varun Chakaravarthy"
        ],
        "ans": 2,
        "exp": "Sunil Narine! The mystery spinner has been KKR's most lethal weapon since he joined the squad in 2012."
    },
    {
        "q": "The name 'Kolkata Knight Riders' was inspired by which famous 1980s American television show?",
        "opts": [
            "Knight Rider",
            "The A-Team",
            "Miami Vice",
            "Airwolf"
        ],
        "ans": 0,
        "exp": "The franchise name was a direct nod to the popular David Hasselhoff show 'Knight Rider'."
    },
    {
        "q": "Before switching to their iconic Purple and Gold in 2010, what were KKR's original team colors?",
        "opts": [
            "Red and Gold",
            "Black and Gold",
            "Blue and Silver",
            "Green and Gold"
        ],
        "ans": 1,
        "exp": "KKR originally wore Black and Gold. The black represented the Goddess Kali, and the gold represented the spirit of life."
    },
    {
        "q": "Which KKR player holds the record for winning the IPL 'Most Valuable Player' (MVP) award three times?",
        "opts": [
            "Gautam Gambhir",
            "Andre Russell",
            "Sunil Narine",
            "Jacques Kallis"
        ],
        "ans": 2,
        "exp": "Sunil Narine is the ultimate MVP! He won the prestigious award in 2012, 2018, and 2024."
    }
],
  legends: [
    {
        "name": "Sourav Ganguly",
        "years": "2008, 2010 (Player/Captain)",
        "achievement": "The Prince of Calcutta and KKR's first-ever icon player. Dada laid the foundation for the franchise as its first captain and remains an absolute legend of Eden Gardens. He also holds the historic distinction of facing the very first delivery in IPL history.",
        "stat": "40 Matches · 1,031 Runs · 8 Wickets",
        "avatar": "images/sourav-ganguly.jpg"
    },
    {
        "name": "Gautam Gambhir",
        "years": "2011 – 2017 (Player/Captain) · 2024 (Mentor)",
        "achievement": "The legendary skipper who transformed KKR. Gambhir captained KKR to their first two IPL trophies in 2012 and 2014, and returned as Mentor in 2024 to guide the team to their third title.",
        "stat": "122 Matches · 3,375 Runs · 2 Titles",
        "avatar": "images/gautam-gambhir.jpg"
    },
    {
        "name": "Jacques Kallis",
        "years": "2011 – 2014 (Player) · 2015 – 2019 (Coach)",
        "achievement": "One of the greatest all-rounders in cricket history. Kallis was KKR's anchor in the 2012 and 2014 championships, scoring crucial half-centuries and taking key wickets.",
        "stat": "98 Matches · 1,603 Runs · 44 Wickets",
        "avatar": "images/jacques-kallis.jpg"
    },
    {
        "name": "Robin Uthappa",
        "years": "2014 – 2019 (Player)",
        "achievement": "The bedrock of KKR's batting order. Robin won the Orange Cap in 2014 with 660 runs (including a record 10 consecutive 40+ scores), playing a monumental role in securing KKR's second trophy.",
        "stat": "86 Matches · 2,439 Runs · 2014 Orange Cap",
        "avatar": "images/robin-uthappa.jpg"
    },
    {
        "name": "Yusuf Pathan",
        "years": "2011 – 2017 (Player)",
        "achievement": "The ultimate explosive finisher of the Purple Army. Pathan played countless high-impact innings, including hitting the fastest fifty in IPL history at the time (15 balls vs SRH in 2014).",
        "stat": "106 Matches · 1,893 Runs · 143.6 S/R",
        "avatar": "images/yusuf-pathan.jpg"
    },
    {
        "name": "Brendon McCullum",
        "years": "2008 – 2010, 2012 – 2013 (Player) · 2020 – 2022 (Coach)",
        "achievement": "The man who started it all. McCullum hit a legendary, unbeaten 158* in the opening match of the inaugural 2008 IPL, writing KKR and the league into global sporting history.",
        "stat": "35 Matches · 881 Runs · 158* High Score",
        "avatar": "images/brendon-mccullum.jpg"
    }
],
  seasons: [
    { year: "2012", w: 13, l: 3, title: true },
    { year: "2013", w: 8, l: 8, title: false },
    { year: "2014", w: 11, l: 3, title: true },
    { year: "2018", w: 6, l: 8, title: false },
    { year: "2019", w: 6, l: 8, title: false },
    { year: "2021", w: 7, l: 7, title: false },
    { year: "2022", w: 6, l: 8, title: false },
    { year: "2023", w: 6, l: 8, title: false },
    { year: "2024", w: 9, l: 5, title: true },
    { year: "2025", w: 8, l: 6, title: false },
    { year: "2026", w: 6, l: 7, title: false }
  ]
};

// Reactive App State
let players = [];
let masterStats = {};
let matches = [];
let newsArticles = [];
let quizQuestions = [];
let legends = [];
let seasons = [];

// DOM References
const playersGrid = document.getElementById("playersGrid");
const playerModal = document.getElementById("playerModal");
const modalContent = document.getElementById("modalContent");
const modalClose = document.getElementById("modalClose");
const scheduleGrid = document.querySelector(".schedule-grid");
const newsGrid = document.querySelector(".news-grid");

/* ============================================================
   DATA LOADING FROM BACKEND API (WITH STATIC CLIENT FALLBACK)
============================================================ */

async function loadBackendData() {
  // Show skeletons loading indicators
  showSkeletons();
  
  let playersFailed = false;

  async function fetchSafe(endpoint, fallbackKey) {
    try {
      const res = await fetch(`${API_URL}/${endpoint}`);
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      console.log(`API success: Loaded /api/${endpoint} successfully.`);
      return data;
    } catch (err) {
      console.error(`API failure: Failed to load /api/${endpoint}.`, err);
      if (endpoint === 'players') {
        playersFailed = true;
      }
      return FALLBACK_DATA[fallbackKey];
    }
  }

  const [resPlayers, resStats, resMatches, resNews, resQuiz, resLegends, resSeasons] = await Promise.all([
    fetchSafe('players', 'players'),
    fetchSafe('players/stats', 'masterStats'),
    fetchSafe('matches', 'matches'),
    fetchSafe('news', 'newsArticles'),
    fetchSafe('quiz', 'quizQuestions'),
    fetchSafe('legends', 'legends'),
    fetchSafe('seasons', 'seasons')
  ]);

  players = resPlayers;
  masterStats = resStats;
  matches = resMatches;
  newsArticles = resNews;
  quizQuestions = resQuiz;
  legends = resLegends;
  seasons = resSeasons;

  if (playersFailed) {
    showOfflineBanner();
    showToast("Server connection offline. Running in static mode.", "warning");
  } else {
    // Backend API is online, remove the persistent offline banner if it exists
    const banner = document.getElementById('offline-banner');
    if (banner) {
      banner.remove();
    }
    showToast("Loaded real-time server database successfully.", "success");
  }

  // Initialize components
  renderRoster();
  renderSchedule();
  renderLegends();
  renderNews();
  buildPerformanceChart();
  initMVPPoll();
  initCheerWall();
  initTriviaQuiz();
}

/* ============================================================
   ROSTER RENDERING, FILTERING & MODALS
============================================================ */

function renderRoster(filterRole = "all") {
  if (!playersGrid) return;
  playersGrid.innerHTML = "";
  
  const filteredPlayers = players.filter(p => {
    if (filterRole === "all") return true;
    return p.role.toLowerCase() === filterRole.toLowerCase();
  });

  filteredPlayers.forEach((p) => {
    const card = document.createElement("div");
    card.className = `player-card reveal visible`;
    
    // Find index of the player in the main array
    const mainIdx = players.indexOf(p);

    // If image is empty, render silhouette placeholder, else render img
    const imageHtml = p.image && p.image !== "" 
      ? `<img class="player-card-img" src="${p.image}" alt="${p.name}" loading="lazy" />`
      : `<div class="player-card-placeholder">
           <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
           </svg>
           <span class="placeholder-jersey-bg">#${p.jersey}</span>
         </div>`;

    card.innerHTML = `
      <div class="player-img-wrap">
        ${imageHtml}
        <span class="player-jersey">#${p.jersey}</span>
      </div>
      <div class="player-info">
        <div class="player-name">${p.name}</div>
        <div class="player-role">${p.role === "Wicketkeeper" ? "WK-Batsman" : p.role}</div>
        <div class="player-stats-row">
          ${p.stats.map(s => `
            <div class="p-stat">
              <span class="p-stat-val">${s.v}</span>
              <span class="p-stat-key">${s.k}</span>
            </div>
          `).join("")}
        </div>
      </div>
    `;
    
    card.addEventListener("click", () => openPlayerModal(mainIdx));
    playersGrid.appendChild(card);
  });
}

function openPlayerModal(idx) {
  if (!modalContent) return;
  const p = players[idx];
  
  // If image is empty, render silhouette placeholder, else render img
  const imageHtml = p.image && p.image !== "" 
    ? `<img class="modal-player-img" src="${p.image}" alt="${p.name}" loading="lazy" />`
    : `<div class="player-card-placeholder modal-placeholder">
         <svg class="placeholder-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
           <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
         </svg>
         <span class="placeholder-jersey-bg" style="font-size: 6rem;">#${p.jersey}</span>
       </div>`;
  
  const fullStats = masterStats[p.name] || p.stats;
  const filteredStatsList = fullStats.filter(s => {
    if ((s.k === "Wickets" || s.k === "Econ") && parseFloat(s.v) === 0) {
      return false;
    }
    if ((s.k === "Runs" || s.k === "Avg" || s.k === "S/R") && p.role.toLowerCase() === "bowler" && parseFloat(fullStats.find(x => x.k === "Runs")?.v || 0) < 50) {
      return false;
    }
    return true;
  });

  modalContent.innerHTML = `
    <div class="modal-profile-wrap">
      <div class="modal-left">
        ${imageHtml}
      </div>
      <div class="modal-right">
        <div class="modal-player-name">${p.name}</div>
        <div class="modal-role">${p.role === "Wicketkeeper" ? "Wicketkeeper-Batsman" : p.role} · ${p.country}</div>
        <p class="modal-bio">${p.bio}</p>
        <div class="modal-stats" style="margin-top: 16px;">
          ${filteredStatsList.map(s => `
            <div class="modal-stat">
              <span class="modal-stat-val">${s.v}</span>
              <span class="modal-stat-key">${s.k}</span>
            </div>
          `).join("")}
          <div class="modal-stat">
            <span class="modal-stat-val">#${p.jersey}</span>
            <span class="modal-stat-key">Jersey</span>
          </div>
        </div>
      </div>
    </div>
  `;
  if (playerModal) {
    playerModal.classList.add("open");
    document.body.style.overflow = "hidden";
  }
}

if (modalClose) {
  modalClose.addEventListener("click", () => {
    if (playerModal) playerModal.classList.remove("open");
    document.body.style.overflow = "";
  });
}

window.addEventListener("click", e => {
  if (e.target === playerModal) {
    playerModal.classList.remove("open");
    document.body.style.overflow = "";
  }
});

// Setup squad filter buttons
const squadFilters = document.querySelectorAll("#squadFilters .filter-tab");
squadFilters.forEach(tab => {
  tab.addEventListener("click", () => {
    squadFilters.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    renderRoster(tab.getAttribute("data-role"));
  });
});

/* ============================================================
   SCHEDULE RENDERING & FILTERING
============================================================ */

function renderSchedule(filterStatus = "all") {
  if (!scheduleGrid) return;
  scheduleGrid.innerHTML = "";

  const filteredMatches = matches.filter(m => {
    if (filterStatus === "all") return true;
    return m.status === filterStatus;
  });

  filteredMatches.forEach(m => {
    const card = document.createElement("div");
    card.className = "match-card reveal visible";
    
    let statusClass = "status-upcoming";
    let statusLabel = "Upcoming";
    
    if (m.status === "won") {
      statusClass = "status-won";
      statusLabel = "Won";
    } else if (m.status === "lost") {
      statusClass = "status-lost";
      statusLabel = "Lost";
    } else if (m.status === "noresult") {
      statusClass = "status-noresult";
      statusLabel = "No Result";
    }

    card.innerHTML = `
      <div class="match-teams">
        <div class="team-badge kkr">KKR</div>
        <span class="match-vs">VS</span>
        <div class="team-badge" style="${m.theme}">${m.vs}</div>
        <div class="match-details">
          <span class="match-title">KKR vs ${m.opp}</span>
          <span class="match-stadium">${m.venue}</span>
        </div>
      </div>
      <div class="match-info">
        <span class="match-date">${m.date}</span>
        <span class="match-time">${m.desc}</span>
        <div class="match-status-wrap">
          <span class="match-status ${statusClass}">${statusLabel}</span>
        </div>
      </div>
    `;
    scheduleGrid.appendChild(card);
  });
}

// Setup schedule filter buttons
const scheduleFilters = document.querySelectorAll("#scheduleFilters .filter-tab");
scheduleFilters.forEach(tab => {
  tab.addEventListener("click", () => {
    scheduleFilters.forEach(t => t.classList.remove("active"));
    tab.classList.add("active");
    renderSchedule(tab.getAttribute("data-status"));
  });
});

/* ============================================================
   NEWS RENDERING
============================================================ */

function renderNews() {
  if (!newsGrid) return;
  newsGrid.innerHTML = "";

  newsArticles.forEach(n => {
    const card = document.createElement("div");
    card.className = "news-card reveal visible";
    
    let backgroundStyle = "";
    if (n.cat === "Squad Update") {
      backgroundStyle = "style='background:linear-gradient(135deg,#1b0045,#0a0014)'";
    } else if (n.cat === "Interview") {
      backgroundStyle = "style='background:linear-gradient(135deg,#2e006c,#0a0014)'";
    } else if (n.cat === "Update") {
      backgroundStyle = "style='background:linear-gradient(135deg,#3c0082,#0a0014)'";
    } else if (n.cat === "Analysis") {
      backgroundStyle = "style='background:linear-gradient(135deg,#4e0099,#0a0014)'";
    }

    card.innerHTML = `
      <div class="news-thumb" ${backgroundStyle}>
        <span class="news-thumb-label">KKR</span>
        <span class="news-cat">${n.cat}</span>
      </div>
      <div class="news-body">
        <div class="news-date">${n.date}</div>
        <h3 class="news-headline">${n.headline}</h3>
        <p class="news-snippet">${n.snippet}</p>
        <a href="${n.link}" class="news-link">Read Story →</a>
      </div>
    `;
    newsGrid.appendChild(card);
  });
}

/* ============================================================
   STATS CHART SCROLL ANIMATION
============================================================ */

function buildPerformanceChart() {
  const chartEl = document.getElementById("perfChart");
  if (!chartEl) return;
  chartEl.innerHTML = "";

  seasons.forEach(s => {
    const total = s.w + s.l;
    const wPct = Math.round((s.w / total) * 100);
    
    const row = document.createElement("div");
    row.className = "chart-row";
    row.innerHTML = `
      <span class="chart-year">${s.year}</span>
      <div class="chart-track">
        <div class="chart-bar" data-width="${wPct}%"></div>
      </div>
      <span class="chart-label">${s.w}W – ${s.l}L${s.title ? ' 🏆' : ''}</span>
    `;
    chartEl.appendChild(row);
  });
}

function animateChart() {
  const chartBars = document.querySelectorAll(".chart-bar");
  chartBars.forEach(bar => {
    const width = bar.getAttribute("data-width");
    bar.style.width = width;
  });
}

/* ============================================================
   FAN ZONE - INTERACTIVE MVP POLL (PERSISTENT VIA SERVER API)
============================================================ */

let pollVotes = [];
let pollVoted = false;
let pollLabels = [];

async function initMVPPoll() {
  const pollOptionsContainer = document.getElementById("pollOptions");
  const pollTotal = document.getElementById("pollTotal");
  if (!pollOptionsContainer) return;

  // Check locally if voted in this session
  if (sessionStorage.getItem("kkr_mvp_voted") === "true") {
    pollVoted = true;
  }

  try {
    const res = await fetch(`${API_URL}/poll`).then(r => r.json());
    pollVotes = res.votes;
    pollLabels = res.labels;
  } catch (err) {
    console.warn("MVP Poll API load failed. Falling back to local data.", err);
    pollLabels = ["Sunil Narine", "Rinku Singh", "Varun Chakravarthy", "Quinton de Kock"];
    pollVotes = JSON.parse(sessionStorage.getItem("kkr_mvp_votes")) || [42, 28, 18, 12];
  }
  renderPollOptions(pollLabels, pollOptionsContainer, pollTotal);
  connectPollWebSocket();
}

function renderPollOptions(labels, container, totalLabel) {
  container.innerHTML = "";
  const totalVotesCount = pollVotes.reduce((a, b) => a + b, 0);

  labels.forEach((lbl, idx) => {
    const btn = document.createElement("button");
    btn.className = `poll-option ${pollVoted ? 'voted' : ''}`;
    btn.setAttribute("data-idx", idx);
    if (pollVoted) btn.disabled = true;

    const pct = totalVotesCount > 0 ? Math.round((pollVotes[idx] / totalVotesCount) * 100) : 0;
    
    btn.innerHTML = `
      <div class="poll-bar" style="width: ${pollVoted ? pct + '%' : '0%'}"></div>
      <span class="poll-opt-label">${lbl}</span>
      <span class="poll-pct" style="display: ${pollVoted ? 'block' : 'none'}">${pct}%</span>
    `;

    if (!pollVoted) {
      btn.addEventListener("click", () => {
        votePoll(idx, labels, container, totalLabel);
      });
    }

    container.appendChild(btn);
  });

  totalLabel.textContent = `${totalVotesCount.toLocaleString()} votes · ${pollVoted ? 'Thank you for voting!' : 'Vote to see live results'}`;
}

async function votePoll(idx, labels, container, totalLabel) {
  if (pollVoted) return;
  pollVoted = true;
  sessionStorage.setItem("kkr_mvp_voted", "true");

  try {
    const res = await fetch(`${API_URL}/poll`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ index: idx })
    }).then(r => r.json());
    pollVotes = res.votes;
  } catch (err) {
    console.warn("MVP Poll API vote post failed. Saving to sessionStorage.", err);
    pollVotes[idx]++;
    sessionStorage.setItem("kkr_mvp_votes", JSON.stringify(pollVotes));
  }

  renderPollOptions(labels, container, totalLabel);
  
  // Add quick animation flare to the selected option
  const selectedBtn = container.querySelector(`[data-idx="${idx}"]`);
  if (selectedBtn) {
    selectedBtn.classList.add("voted");
    selectedBtn.style.boxShadow = "0 0 15px rgba(245, 197, 24, 0.4)";
  }
}

/* ============================================================
   FAN ZONE - CHEER WALL (PERSISTENT VIA SERVER API)
============================================================ */

async function initCheerWall() {
  const wall = document.getElementById("fanWall");
  const postBtn = document.getElementById("fanPost");
  const nameInput = document.getElementById("fanNameInput");
  const msgInput = document.getElementById("fanMsgInput");

  if (!wall) return;

  let cheers = [];

  const defaultCheers = [
    { name: "Debashish P.", msg: "KKR forever! Eden Gardens was thunder in 2026! 💜", time: "May 24" },
    { name: "Priya K.", msg: "Rinku bhai did his best as vice-captain! Super proud! 💜💛", time: "May 24" },
    { name: "Arjun S.", msg: "Narine mystery never ends, 14 years of greatness. 🐐", time: "May 23" },
    { name: "Mita D.", msg: "Korbo Lorbo Jeetbo! We will come back stronger in 2027! 🏆", time: "May 23" }
  ];

  async function fetchCheers() {
    try {
      cheers = await fetch(`${API_URL}/cheers`).then(r => r.json());
    } catch (err) {
      console.warn("Cheer Wall API fetch failed. Falling back to localStorage.", err);
      cheers = JSON.parse(localStorage.getItem("kkr_cheers")) || defaultCheers;
    }
    displayCheers();
  }

  function displayCheers() {
    wall.innerHTML = "";
    cheers.forEach(c => {
      const msgBox = document.createElement("div");
      msgBox.className = "cheer-msg";
      msgBox.innerHTML = `
        <span class="cheer-name">${c.name}</span>
        <span class="cheer-time">${c.time}</span>
        <p style="margin-top: 4px; color: var(--text-main);">${c.msg}</p>
      `;
      wall.appendChild(msgBox);
    });
  }

  await fetchCheers();

  connectCheersWebSocket((updatedCheers) => {
    cheers = updatedCheers;
    displayCheers();
  });

  if (postBtn) {
    postBtn.addEventListener("click", async () => {
      const name = nameInput.value.trim();
      const msg = msgInput.value.trim();

      if (!name) {
        alert("Please enter your name!");
        nameInput.focus();
        return;
      }
      if (!msg) {
        alert("Please enter a cheer message!");
        msgInput.focus();
        return;
      }

      try {
        const res = await fetch(`${API_URL}/cheers`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, msg })
        }).then(r => r.json());

        cheers = res;
      } catch (err) {
        console.warn("Cheer Wall API post failed. Saving to localStorage.", err);
        const now = new Date();
        const dateString = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        const newCheer = { name, msg, time: dateString };
        cheers.unshift(newCheer);
        if (cheers.length > 30) cheers.pop();
        localStorage.setItem("kkr_cheers", JSON.stringify(cheers));
      }

      displayCheers();
      msgInput.value = "";
    });

    msgInput.addEventListener("keydown", e => {
      if (e.key === "Enter") postBtn.click();
    });
  }
}

/* ============================================================
   FAN ZONE - TRIVIA QUIZ
============================================================ */

let currentQuizIdx = 0;
let quizScore = 0;

function initTriviaQuiz() {
  const container = document.getElementById("triviaQuizContainer");
  if (!container) return;

  renderQuizQuestion(container);
}

function renderQuizQuestion(container) {
  container.innerHTML = "";
  
  if (currentQuizIdx >= quizQuestions.length) {
    renderQuizResults(container);
    return;
  }

  const qData = quizQuestions[currentQuizIdx];
  const qBox = document.createElement("div");
  qBox.className = "quiz-container reveal visible";
  
  qBox.innerHTML = `
    <div class="quiz-card">
      <div class="quiz-header-row">
        <span class="quiz-question-num">Question ${currentQuizIdx + 1} of ${quizQuestions.length}</span>
        <span class="quiz-score-badge">Score: ${quizScore}/${quizQuestions.length}</span>
      </div>
      <div class="quiz-question">${qData.q}</div>
      <div class="quiz-options">
        ${qData.opts.map((opt, idx) => `
          <button class="quiz-opt" data-idx="${idx}">${opt}</button>
        `).join("")}
      </div>
      <div class="quiz-feedback" id="quizFeedback"></div>
    </div>
  `;

  container.appendChild(qBox);

  // Handle Option Clicks
  const optionBtns = qBox.querySelectorAll(".quiz-opt");
  optionBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const selectedIdx = parseInt(btn.getAttribute("data-idx"));
      handleQuizAnswer(selectedIdx, optionBtns, qData);
    });
  });
}

function handleQuizAnswer(selectedIdx, optionBtns, qData) {
  const feedbackEl = document.getElementById("quizFeedback");
  const container = document.getElementById("triviaQuizContainer");
  
  // Disable all options immediately
  optionBtns.forEach(btn => {
    btn.classList.add("disabled");
    const idx = parseInt(btn.getAttribute("data-idx"));
    if (idx === qData.ans) {
      btn.classList.add("correct");
    }
  });

  if (selectedIdx === qData.ans) {
    quizScore++;
    feedbackEl.className = "quiz-feedback correct";
    feedbackEl.textContent = `Correct! ${qData.exp}`;
  } else {
    optionBtns[selectedIdx].classList.add("incorrect");
    feedbackEl.className = "quiz-feedback incorrect";
    feedbackEl.textContent = `Wrong! ${qData.exp}`;
  }

  // Move to next question after 4 seconds
  setTimeout(() => {
    currentQuizIdx++;
    renderQuizQuestion(container);
  }, 4200);
}

function renderQuizResults(container) {
  let praise = "Purple Soldier 💜";
  if (quizScore === quizQuestions.length) praise = "Ultimate Knight Rider Champion! 🏆";
  else if (quizScore >= 1) praise = "Dedicated KKR Supporter! 🌟";

  container.innerHTML = `
    <div class="quiz-results-card reveal visible">
      <div class="quiz-question-num">Quiz Completed</div>
      <div class="quiz-results-score">${quizScore} / ${quizQuestions.length}</div>
      <div class="quiz-results-msg">
        <strong>${praise}</strong><br>
        Thank you for playing the KKR Trivia Quiz! Show off your score on the Fan Wall!
      </div>
      <button class="btn-primary" id="restartQuizBtn" style="font-size: 0.85rem; padding: 10px 22px;">Play Again</button>
    </div>
  `;

  document.getElementById("restartQuizBtn").addEventListener("click", () => {
    currentQuizIdx = 0;
    quizScore = 0;
    renderQuizQuestion(container);
  });
}

/* ============================================================
   FAN ZONE - CHANT GENERATOR & SYNTHESIZER
============================================================ */

function initChantGenerator() {
  const chantBtn = document.getElementById("playChantBtn");
  const waves = document.getElementById("chantWaves");
  const chantBox = document.getElementById("chantBox");

  if (!chantBtn || !waves) return;

  const chants = [
    "KORBO LORBO JEETBO RE! 🏆",
    "💜 PURPLE ARMY! 💛",
    "EDEN GARDENS IN THE HOUSE! 🏟️",
    "AMI KKR! 🏏",
    "RINKU FINISHES IT IN STYLE! ⚡",
    "NARINE MYSTERY SPINS AGAIN! 🌀",
    "DRE RUSS SHOW! 💪"
  ];

  chantBtn.addEventListener("click", () => {
    // Enable visual wave bouncing
    waves.classList.add("playing");
    chantBtn.textContent = "Chanting...";
    chantBtn.disabled = true;

    // Play retro synthesizer audio chant
    playSynthesizerChant();

    // Create 5 floating text tags randomly scattered
    for (let i = 0; i < 5; i++) {
      setTimeout(() => {
        createFloatingChant(chants[Math.floor(Math.random() * chants.length)], chantBox);
      }, i * 250);
    }

    // Stop visual waves after 2.5 seconds
    setTimeout(() => {
      waves.classList.remove("playing");
      chantBtn.textContent = "Cheer KKR Chant!";
      chantBtn.disabled = false;
    }, 2500);
  });
}

function createFloatingChant(text, parent) {
  const el = document.createElement("div");
  el.className = "chant-bubble";
  el.textContent = text;
  
  const randX = Math.floor(Math.random() * 200) - 100;
  const randLeft = 30 + Math.floor(Math.random() * 40);
  const randRotate = Math.floor(Math.random() * 30) - 15;
  const randScale = 0.8 + (Math.random() * 0.5);

  el.style.left = `${randLeft}%`;
  el.style.top = `60%`;
  el.style.transform = `rotate(${randRotate}deg) scale(${randScale})`;
  el.style.setProperty("--float-x", `${randX}px`);

  parent.appendChild(el);

  setTimeout(() => {
    el.remove();
  }, 1300);
}

let audioCtx = null;

function playSynthesizerChant() {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }
  
  const now = audioCtx.currentTime;
  
  const notes = [
    { freq: 261.63, time: 0.0, dur: 0.15 }, // Kor
    { freq: 329.63, time: 0.25, dur: 0.15 }, // bo
    { freq: 293.66, time: 0.5, dur: 0.15 }, // Lor
    { freq: 349.23, time: 0.75, dur: 0.15 }, // bo
    { freq: 392.00, time: 1.0, dur: 0.35 }, // Jeet
    { freq: 329.63, time: 1.4, dur: 0.15 }, // bo
    { freq: 261.63, time: 1.6, dur: 0.60 }  // Re!
  ];
  
  notes.forEach(note => {
    playSynthNote(note.freq, now + note.time, note.dur);
  });
}

function playSynthNote(freq, startTime, duration) {
  if (!audioCtx) return;
  
  const osc = audioCtx.createOscillator();
  const gainNode = audioCtx.createGain();
  
  osc.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  
  osc.type = "triangle";
  osc.frequency.setValueAtTime(freq, startTime);
  
  gainNode.gain.setValueAtTime(0, startTime);
  gainNode.gain.linearRampToValueAtTime(0.25, startTime + 0.02);
  gainNode.gain.exponentialRampToValueAtTime(0.001, startTime + duration);
  
  osc.start(startTime);
  osc.stop(startTime + duration);
}



/* ============================================================
   EDEN GARDENS SEAT BOOKER
============================================================ */

function initSeatBooker() {
  const stands = document.querySelectorAll(".stadium-stand");
  const bookingPanel = document.getElementById("bookingPanel");
  
  if (!bookingPanel) return;
  
  let selectedStand = null;
  let selectedPrice = null;
  
  const originalFormHTML = bookingPanel.innerHTML;
  
  function bindFormEvents() {
    const currentBookBtn = document.getElementById("btnBookTicket");
    const currentNameInput = document.getElementById("bookingName");
    
    if (currentBookBtn) {
      currentBookBtn.addEventListener("click", () => {
        const userName = currentNameInput.value.trim();
        if (!userName) {
          alert("Please enter your name to book the ticket!");
          currentNameInput.focus();
          return;
        }
        if (!selectedStand) {
          alert("Please select a stand from the map first!");
          return;
        }
        
        bookingPanel.innerHTML = `
          <div class="ticket-card" style="animation: ticketReveal 0.6s ease-out forwards;">
            <div class="ticket-header">
              <div class="ticket-logo">KKR RIDE</div>
              <span class="ticket-type">IPL 2026</span>
            </div>
            <div class="ticket-body">
              <div class="ticket-row" style="margin-bottom: 12px;">
                <div>
                  <span class="ticket-label" style="display:block;">Name</span>
                  <div class="ticket-value">${userName}</div>
                </div>
                <div style="text-align: right;">
                  <span class="ticket-label" style="display:block;">Stand</span>
                  <div class="ticket-value highlight">${selectedStand}</div>
                </div>
              </div>
              <div class="ticket-row">
                <div>
                  <span class="ticket-label" style="display:block;">Price</span>
                  <div class="ticket-value">₹${selectedPrice}</div>
                </div>
                <div style="text-align: right;">
                  <span class="ticket-label" style="display:block;">Venue</span>
                  <div class="ticket-value">Eden Gardens</div>
                </div>
              </div>
            </div>
            <div class="ticket-footer">
              <div class="ticket-barcode">
                <div class="barcode-line" style="width:2px; margin-right:2px; background:black;"></div>
                <div class="barcode-line" style="width:1px; margin-right:3px; background:black;"></div>
                <div class="barcode-line" style="width:4px; margin-right:1px; background:black;"></div>
                <div class="barcode-line" style="width:2px; margin-right:2px; background:black;"></div>
                <div class="barcode-line" style="width:1px; margin-right:2px; background:black;"></div>
                <div class="barcode-line" style="width:3px; margin-right:4px; background:black;"></div>
                <div class="barcode-line" style="width:2px; margin-right:1px; background:black;"></div>
                <div class="barcode-line" style="width:1px; margin-right:1px; background:black;"></div>
                <div class="barcode-line" style="width:4px; background:black;"></div>
              </div>
              <button class="btn-primary" id="btnBookAnother" style="padding: 8px 14px; font-size: 0.75rem;">Book Another</button>
            </div>
            <div class="ticket-stamp">CONFIRMED</div>
          </div>
        `;
        
        document.getElementById("btnBookAnother").addEventListener("click", () => {
          stands.forEach(s => s.classList.remove("selected"));
          selectedStand = null;
          selectedPrice = null;
          
          bookingPanel.innerHTML = originalFormHTML;
          bindFormEvents();
        });
      });
    }
  }
  
  stands.forEach(stand => {
    stand.addEventListener("click", () => {
      stands.forEach(s => s.classList.remove("selected"));
      stand.classList.add("selected");
      
      selectedStand = stand.getAttribute("data-stand");
      selectedPrice = stand.getAttribute("data-price");
      
      const currentSelectedStandLabel = document.getElementById("bookingSelectedStand");
      const currentPriceLabel = document.getElementById("bookingPrice");
      const currentBookBtn = document.getElementById("btnBookTicket");
      
      if (currentSelectedStandLabel) currentSelectedStandLabel.textContent = selectedStand;
      if (currentPriceLabel) currentPriceLabel.textContent = `₹${selectedPrice}`;
      if (currentBookBtn) {
        currentBookBtn.disabled = false;
        currentBookBtn.textContent = `Book ${selectedStand} Now`;
      }
    });
  });
  
  bindFormEvents();
}

/* ============================================================
   TEAM LEGENDS SECTION
============================================================ */

function renderLegends() {
  const container = document.getElementById("legendsGrid");
  if (!container) return;
  container.innerHTML = "";
  
  legends.forEach(l => {
    const card = document.createElement("div");
    card.className = "legend-card reveal visible";
    
    const imageHtml = l.avatar && l.avatar !== ""
      ? `<img class="legend-img" src="${l.avatar}" alt="${l.name}" loading="lazy" />`
      : `<div class="legend-avatar-placeholder">
           <svg class="legend-placeholder-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
             <path d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z" fill="currentColor"/>
           </svg>
         </div>`;

    card.innerHTML = `
      <div class="legend-avatar-wrap">
        ${imageHtml}
      </div>
      <div class="legend-name">${l.name}</div>
      <div class="legend-years">${l.years}</div>
      <p class="legend-achievement">${l.achievement}</p>
      <span class="legend-stat-badge">${l.stat}</span>
    `;
    container.appendChild(card);
  });
}

/* ============================================================
   SCROLL PROGRESS & NAV SCROLL
============================================================ */

function initScrollEffects() {
  const progressBar = document.getElementById("scroll-progress");
  const navbar = document.getElementById("navbar");
  
  window.addEventListener("scroll", () => {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
    if (progressBar) progressBar.style.width = scrolled + "%";

    if (navbar) {
      if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
      } else {
        navbar.classList.remove("scrolled");
      }
    }
  });
}

/* ============================================================
   HAMBURGER MENU & BACK TO TOP
============================================================ */

function initNavAndBtt() {
  const hamburger = document.getElementById("hamburger");
  const navLinks = document.getElementById("navLinks");
  
  if (hamburger && navLinks) {
    hamburger.addEventListener("click", () => {
      hamburger.classList.toggle("open");
      navLinks.classList.toggle("open");
    });

    navLinks.querySelectorAll("a").forEach(a => {
      a.addEventListener("click", () => {
        hamburger.classList.remove("open");
        navLinks.classList.remove("open");
      });
    });
  }

  const btt = document.getElementById("btt");
  if (btt) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 400) {
        btt.classList.add("show");
      } else {
        btt.classList.remove("show");
      }
    });
    
    btt.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
}

/* ============================================================
   SCROLL REVEAL OBSERVER
============================================================ */

function initScrollReveal() {
  const revealEls = document.querySelectorAll(".reveal");
  
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add("visible");
        
        if (e.target.id === "stats" || e.target.contains(document.getElementById("perfChart"))) {
          setTimeout(animateChart, 200);
        }
        
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.1 });

  revealEls.forEach(el => io.observe(el));
}

/* ============================================================
   ANTI-GRAVITY PARTICLE BACKGROUND EFFECT (GOLD & PURPLE THEME)
============================================================ */

function initParticleBackground() {
  const canvas = document.getElementById("bg");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const particles = [];
  const particleCount = 75;
  
  // Reference to logo image for particle emissions
  const logo = document.querySelector(".nav-logo");
  const heroBadge = document.getElementById("heroBadge");
  let isLogoHovered = false;
  let isHeroHovered = false;

  if (logo) {
    logo.addEventListener("mouseenter", () => { isLogoHovered = true; });
    logo.addEventListener("mouseleave", () => { isLogoHovered = false; });
  }
  if (heroBadge) {
    heroBadge.addEventListener("mouseenter", () => { isHeroHovered = true; });
    heroBadge.addEventListener("mouseleave", () => { isHeroHovered = false; });
  }

  class Particle {
    constructor(fromLogo = false) {
      this.fromLogo = fromLogo;
      this.reset();
      
      // If initialized at startup and not from logo, distribute randomly
      if (!fromLogo) {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
      }
    }

    reset() {
      if (this.fromLogo) {
        if (isHeroHovered && heroBadge) {
          const rect = heroBadge.getBoundingClientRect();
          // Spawn around the hero badge coordinates
          this.x = rect.left + rect.width / 2 + (Math.random() - 0.5) * 60;
          this.y = rect.top + rect.height / 2 + (Math.random() - 0.5) * 60;
          this.size = Math.random() * 2.2 + 0.6;
          
          // Flow upwards and outwards from the hero badge
          this.speedX = (Math.random() - 0.5) * 3;
          this.speedY = -(Math.random() * 2 + 1);
        } else if (logo) {
          const rect = logo.getBoundingClientRect();
          // Spawn around the logo coordinates
          this.x = rect.left + rect.width / 2 + (Math.random() - 0.5) * 15;
          this.y = rect.top + rect.height / 2 + (Math.random() - 0.5) * 15;
          this.size = Math.random() * 1.8 + 0.5;
          
          // Flow downwards and outwards from logo
          this.speedX = (Math.random() - 0.5) * 2;
          this.speedY = Math.random() * 1.5 + 0.8;
        } else {
          this.size = 0;
        }
      } else {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 1;
        this.speedX = (Math.random() - 0.5) * 0.8;
        this.speedY = (Math.random() - 0.5) * 0.8;
        this.fromLogo = false;
      }
    }

    update() {
      this.x += this.speedX;
      this.y += this.speedY;

      if (this.fromLogo) {
        // Logo particles slowly fade out
        this.size -= 0.015;
        if (this.size <= 0) {
          this.reset();
        }
      } else {
        // Normal particles move upwards (anti-gravity)
        this.y -= 0.18;

        if (this.y < 0) {
          this.y = canvas.height;
          this.x = Math.random() * canvas.width;
        }

        if (this.x > canvas.width || this.x < 0) {
          this.speedX *= -1;
        }
      }
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
      ctx.fillStyle = this.fromLogo ? "rgba(245, 197, 24, 0.85)" : "rgba(245, 197, 24, 0.65)";
      ctx.fill();
    }
  }

  // Normal background particles
  for (let i = 0; i < particleCount; i++) {
    particles.push(new Particle(false));
  }

  // Logo specific particles
  const logoParticles = [];
  const maxLogoParticles = 40;

  function connectParticles() {
    // Connect both normal and logo particles
    const allParticles = [...particles, ...logoParticles];
    for (let a = 0; a < allParticles.length; a++) {
      for (let b = a; b < allParticles.length; b++) {
        let dx = allParticles[a].x - allParticles[b].x;
        let dy = allParticles[a].y - allParticles[b].y;
        let distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 110) {
          ctx.strokeStyle = `rgba(150, 0, 255, ${0.15 * (1 - distance / 110)})`;
          ctx.lineWidth = 0.8;
          ctx.beginPath();
          ctx.moveTo(allParticles[a].x, allParticles[a].y);
          ctx.lineTo(allParticles[b].x, allParticles[b].y);
          ctx.stroke();
        }
      }
    }
  }

  let spawnTimer = 0;

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Spawn new logo particles continuously if logo or hero badge is present
    if (logo || heroBadge) {
      spawnTimer++;
      const spawnRate = (isLogoHovered || isHeroHovered) ? 2 : 8; // Spawn more when hovered
      if (spawnTimer % spawnRate === 0 && logoParticles.length < maxLogoParticles) {
        logoParticles.push(new Particle(true));
      }
    }

    // Update & draw normal particles
    particles.forEach((p) => {
      p.update();
      p.draw();
    });

    // Update & draw logo particles (and filter out dead ones)
    for (let i = logoParticles.length - 1; i >= 0; i--) {
      const lp = logoParticles[i];
      lp.update();
      if (lp.size <= 0) {
        logoParticles.splice(i, 1);
      } else {
        lp.draw();
      }
    }

    connectParticles();
    requestAnimationFrame(animate);
  }

  animate();

  window.addEventListener("resize", () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  });
}

/* ============================================================
   CUSTOM CURSOR LOGIC
============================================================ */

function initCustomCursor() {
  const cursorDot = document.getElementById("custom-cursor-dot");
  const cursorOutline = document.getElementById("custom-cursor-outline");

  if (!cursorDot || !cursorOutline) return;

  let mouseX = 0;
  let mouseY = 0;
  let outlineX = 0;
  let outlineY = 0;
  let isMoving = false;

  window.addEventListener("mousemove", e => {
    mouseX = e.clientX;
    mouseY = e.clientY;
    
    if (!isMoving) {
      isMoving = true;
      cursorDot.style.opacity = "1";
      cursorOutline.style.opacity = "1";
    }
  });

  function animateCursor() {
    cursorDot.style.left = mouseX + "px";
    cursorDot.style.top = mouseY + "px";

    outlineX += (mouseX - outlineX) * 0.16;
    outlineY += (mouseY - outlineY) * 0.16;

    cursorOutline.style.left = outlineX + "px";
    cursorOutline.style.top = outlineY + "px";

    requestAnimationFrame(animateCursor);
  }
  requestAnimationFrame(animateCursor);

  document.addEventListener("mouseleave", () => {
    cursorDot.style.opacity = "0";
    cursorOutline.style.opacity = "0";
    isMoving = false;
  });

  document.addEventListener("mouseover", e => {
    const target = e.target;
    if (target.closest("a, button, select, .stadium-stand, .player-card, .legend-card, .poll-option, .quiz-opt, .filter-tab, .social-btn, .modal-close, #btt")) {
      cursorDot.classList.add("hovered");
      cursorOutline.classList.add("hovered");
    } else {
      cursorDot.classList.remove("hovered");
      cursorOutline.classList.remove("hovered");
    }
  });
}

/* ============================================================
   INITIALIZATION
============================================================ */

document.addEventListener("DOMContentLoaded", () => {
  // Load backend data dynamically (resilient to connection errors)
  loadBackendData();
  
  // Initialize frontend specific features
  initSeatBooker();
  initChantGenerator();
  initParticleBackground();
  initCustomCursor();
  
  initScrollEffects();
  initNavAndBtt();
  initScrollReveal();
});
