import { useEffect } from "react";
import "./particles.css";

function Particles({
    quantity = 40,
    color = "#00adb5",
    speed = 2,
    lineDistance = 150
}) {
    useEffect(() => {
        if (!window.particlesJS) {
            console.error("particles.js não foi carregado.");
            return;
        }

        window.particlesJS("particles-js", {
            particles: {
                number: {
                    value: quantity,
                    density: {
                        enable: true,
                        value_area: 800
                    }
                },

                color: {
                    value: color
                },

                shape: {
                    type: "circle",

                    stroke: {
                        width: 1,
                        color: color
                    },

                    polygon: {
                        nb_sides: 6
                    },

                    image: {
                        src: "img/github.svg",
                        width: 100,
                        height: 100
                    }
                },

                opacity: {
                    value: 0.5,
                    random: false,

                    anim: {
                        enable: false,
                        speed: 1,
                        opacity_min: 0.1,
                        sync: false
                    }
                },

                size: {
                    value: 3,
                    random: true,

                    anim: {
                        enable: false,
                        speed: 40,
                        size_min: 0.1,
                        sync: false
                    }
                },

                line_linked: {
                    enable: true,
                    distance: lineDistance,
                    color: color,
                    opacity: 0.4,
                    width: 1
                },

                move: {
                    enable: true,
                    speed: speed,
                    direction: "none",
                    random: false,
                    straight: false,
                    out_mode: "out",
                    bounce: false,

                    attract: {
                        enable: false,
                        rotateX: 600,
                        rotateY: 1200
                    }
                }
            },

            interactivity: {
                detect_on: "window",

                events: {
                    onhover: {
                        enable: false,
                        mode: "repulse"
                    },

                    onclick: {
                        enable: false,
                        mode: "push"
                    },

                    resize: true
                },

                modes: {
                    grab: {
                        distance: 400,

                        line_linked: {
                            opacity: 1
                        }
                    },

                    bubble: {
                        distance: 827.17,
                        size: 40,
                        duration: 2,
                        opacity: 8,
                        speed: 3
                    },

                    repulse: {
                        distance: 679.32,
                        duration: 0.4
                    },

                    push: {
                        particles_nb: 4
                    },

                    remove: {
                        particles_nb: 2
                    }
                }
            },

            retina_detect: true
        });

        return () => {
            const container = document.getElementById("particles-js");

            if (container) {
                container.innerHTML = "";
            }
        };
    }, [quantity, color, speed, lineDistance]);

    return <div id="particles-js"></div>;
}

export default Particles;