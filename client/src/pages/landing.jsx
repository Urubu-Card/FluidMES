import {  Link } from 'react-router-dom'
import DarkVeil from './components/DarkVeil/DarkVeil'
import RotatingText from './components/RotatingText/RotatingText'
import Ferrofluid from './components/Ferrofluid/Ferrofluid';
import CardNav from './components/NavBar/navbar'
import logo from '../../public/logo/logo.svg';

const items = [
    {
      label: "Sobre",
      bgColor: "#3E7DFF",
      textColor: "#fff",
      links: [
        { label: "Home", ariaLabel: "About Company",href:'https://www.google.com/' },
        { label: "Sobre", ariaLabel: "About Company",href:'https://www.google.com/' },
        { label: "Funcionalidades", ariaLabel: "About Company",href:'https://www.google.com/' }
      ]
    },
    {
      label: "O Amanhã", 
      bgColor: "#2E4E99",
      textColor: "#fff",
      links: [
        { label: "NAUTILUS", ariaLabel: "Featured Projects" },
      ]
    },
    {
      label: "Contato",
      bgColor: "#2E4E99", 
      textColor: "#fff",
      links: [
        { label: "Email", ariaLabel: "Email us" },
        { label: "GitHub", ariaLabel: "Gitgub" },
        { label: "LinkedIn", ariaLabel: "LinkedIn" }
      ]
    }
  ];


function Landing() {
    return (
        <div className="landing-page">
            <CardNav
                logo={logo}
                logoAlt="Company Logo"
                items={items}
                baseColor="#24282e"
                menuColor="#DBF3FF"
                buttonBgColor="#3E7DFF"
                buttonTextColor="#DBF3FF"
                ease="circ.out"
                theme="dark"
            />

            <div className="background-fluid">
                <Ferrofluid
                    colors={["#2E4E99","#3E7DFF","#DBF3FF"]}
                    speed={0.1}
                    scale={1.6}
                    turbulence={1}
                    fluidity={0.15}
                    rimWidth={0.2}
                    sharpness={2.5}
                    shimmer={1.5}
                    glow={3}
                    flowDirection="down"
                    opacity={1}
                    mouseInteraction ={false}
                />
                
            </div>

            <div className="content">
                {/* Tudo que você colocar aqui ficará acima do DarkVeil */}

                <Link to="/auth" className="start-button">
                    Começar Agora
                </Link>
                <div className='titulo'>
                    <h1>Fluid
                        <span>
                            <RotatingText
                                texts={[' é inovação', ' é controle', ' é gestão', 'MES']}
                                mainClassName="px-2 sm:px-2 md:px-3 text-black overflow-hidden py-0.5 sm:py-1 md:py-2 justify-center rounded-lg"
                                style = {{backgroundColor: '#2E4E99'}}                                
                                staggerFrom="center"
                                initial={{ y: "100%" }}
                                animate={{ y: 0 }}
                                exit={{ y: "-120%" }}
                                staggerDuration={0.02}
                                splitLevelClassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
                                transition={{ type: "spring", damping: 20, stiffness: 500 }}
                                rotationInterval={1500}
                                splitBy="lines"
                                auto
                                loop = {false}
                            />
                        </span>
                    </h1>
                </div>
            </div>
            <div className='conteudo-abaixo' >
                
                <h1>Lorem ipsum dolor sit amet consectetur adipisicing elit. Voluptatum possimus natus corrupti odit voluptate, ad ratione minus, aliquam ex libero nostrum, officia dolorum facere eaque numquam porro? Repellat, optio beatae.</h1>  
                <h1>Lorem ipsum dolor sit amet consectetur adipisicing elit. Laborum velit molestiae quos soluta doloribus in fugit, ipsum alias sequi voluptates facilis maiores sed, libero ullam, odit inventore sunt assumenda provident!</h1>
                <h1>Qui eos ducimus optio aperiam possimus perspiciatis blanditiis, numquam tempore, quibusdam placeat odio facilis. Explicabo provident aut alias, odit nihil excepturi, nesciunt officiis voluptate optio, temporibus pariatur. Cupiditate, ipsam est.</h1>
                <h1>Veritatis iure reiciendis, nobis cumque at repellendus adipisci ipsam commodi ab. Qui vero at sequi non beatae dicta animi inventore, sapiente corrupti pariatur facilis id asperiores repellendus. Reprehenderit, optio rem.</h1>
                <h1>Et omnis blanditiis culpa praesentium pariatur, repellendus consectetur tempore id, odio repellat iure voluptatibus velit quos consequatur eaque asperiores quasi tempora enim, ipsam reprehenderit ipsum. At eius ut quis odio.</h1>
                <h1>Nulla quo eum autem ex molestiae dolorem mollitia atque aliquid dignissimos possimus incidunt voluptate nisi voluptatem quasi necessitatibus quibusdam voluptas quidem, nemo iure ea natus nobis provident assumenda accusantium? Soluta.</h1>
                <h1>Eum, asperiores alias debitis, a dicta molestias commodi quae in recusandae harum illum et animi cum, explicabo sapiente itaque consequuntur. Pariatur maxime hic sequi beatae asperiores, dolores labore expedita quasi!</h1>
                <h1>Expedita ducimus voluptate consequuntur tempore, at itaque, aut ab, asperiores nesciunt dignissimos nulla nam minima suscipit illum. Optio velit laborum repellendus? Alias dolor nihil iste tenetur ea error consequuntur praesentium!</h1>
                <h1>Dolorem, placeat, optio magni nesciunt amet quaerat enim vitae ut beatae quibusdam qui voluptatem voluptatum eos, mollitia consectetur eaque corrupti. Eaque enim fugit, officia expedita totam est cum quidem laborum.</h1>
                <h1>Molestiae distinctio excepturi suscipit omnis dicta, neque tempore autem illum odit iure enim cupiditate optio, consectetur ad. Odit earum corporis fuga? Unde totam ducimus, nemo cum neque minima aspernatur laudantium.</h1>
                <h1>Quas, beatae inventore minus, quae odit nam aliquam adipisci, dolores voluptatem eveniet voluptate nemo molestias nostrum. Veniam consequatur optio architecto necessitatibus voluptatem. Quaerat nisi fugiat magnam molestias aperiam at eligendi?</h1>
            </div>
            

        </div>
    )
}

export default Landing
