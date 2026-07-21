import Link from 'next/link';
import { ChevronLeft, HelpCircle, Database, BrainCircuit, Telescope, FileText, Atom, Sparkles } from 'lucide-react';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#0a0a0f] text-slate-200 font-sans relative overflow-hidden pb-20">
      {/* Background Nebula Effects */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
      <div className="absolute bottom-0 left-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none mix-blend-screen" />

      <main className="max-w-4xl mx-auto p-8 relative z-10 flex flex-col gap-8 mt-10">
        <Link href="/" className="flex items-center gap-2 text-purple-400 hover:text-purple-300 transition-colors w-fit font-medium">
          <ChevronLeft className="w-5 h-5" />
          Volver al Dashboard
        </Link>
        
        <header className="border-b border-white/10 pb-8">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent tracking-tight flex items-center gap-4">
            <HelpCircle className="w-10 h-10 text-purple-400" />
            Ciencia y Metodología (Q&A)
          </h1>
          <p className="text-slate-400 mt-4 text-lg">
            Conoce los fundamentos astrofísicos, la tubería de datos y la arquitectura de Machine Learning que potencian AstroLens.
          </p>
        </header>

        <div className="flex flex-col gap-8">
          {/* Section 1 */}
          <section className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-3 mb-4">
              <Database className="w-6 h-6 text-blue-400" />
              Adquisición de Datos y Catálogo SDSS
            </h2>
            <div className="text-slate-300 space-y-3 leading-relaxed">
              <p>
                La inferencia del modelo depende de datos primarios obtenidos del <strong>Sloan Digital Sky Survey (SDSS)</strong>. A través de la librería <code>astroquery</code>, el backend interroga la base de datos de SDSS para extraer recortes (<em>cutouts</em>) de imágenes FITS en la banda fotométrica <em>g</em> (verde, λ ≈ 4770 Å).
              </p>
              <p>
                Simultáneamente, se realiza un cruce posicional cruzando las tablas <code>PhotoObj</code> y <code>SpecObj</code> para extraer metadatos astrofísicos vitales: la Magnitud Aparente de Modelo (<code>modelMag_g</code>), el tipo morfológico primario, y el corrimiento al rojo (<em>Redshift</em>, z), priorizando el espectroscópico (z<sub>spec</sub>) sobre el fotométrico (z<sub>phot</sub>) por su menor margen de error (Δz ≈ 0.0001).
              </p>
            </div>
          </section>

          {/* Section 2 */}
          <section className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-3 mb-4">
              <BrainCircuit className="w-6 h-6 text-purple-400" />
              Arquitectura de Red Neuronal y Domain Randomization
            </h2>
            <div className="text-slate-300 space-y-3 leading-relaxed">
              <p>
                Dado que los sistemas de Lentes Gravitacionales Fuertes son estadísticamente raros (densidad superficial de ~1 por grado cuadrado), el modelo se entrena utilizando <strong>Domain Randomization</strong> mediante la inyección de datos sintéticos sobre fondos reales.
              </p>
              <p>
                Utilizamos <code>lenstronomy</code> para resolver la Ecuación de la Lente (β = θ - α(θ)) asumiendo un perfil de masa de Elipsoide Isotérmico Singular (SIE) para la galaxia deflectora y perfiles de Sérsic para la galaxia fuente. Estos anillos y arcos de Einstein matemáticamente perfectos se inyectan sobre <strong>recortes de cielo real estocásticos de SDSS</strong> para cerrar el <em>Sim-to-Real Gap</em>. 
              </p>
              <p>
                Para evitar el sesgo inductivo (<em>Data Leakage</em>), el flujo total de fotones (flux) se normaliza rígidamente en ambas clases. Esto fuerza a la red neuronal convolucional (una arquitectura <strong>ResNet-18</strong> modificada) a converger aprendiendo invarianzas morfológicas puras (topología de arcos y anillos espaciales) en lugar de depender de heurísticas triviales de brillo superficial.
              </p>
            </div>
          </section>

          {/* Section 3 */}
          <section className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-3 mb-4">
              <Sparkles className="w-6 h-6 text-pink-400" />
              Interpretabilidad del Modelo (AI Vision)
            </h2>
            <div className="text-slate-300 space-y-3 leading-relaxed">
              <p>
                Las Redes Neuronales Convolucionales (CNNs) son cajas negras por naturaleza. El componente "AI Vision" tiene como objetivo proporcionar <em>Saliency Maps</em> (Mapas de Prominencia) para garantizar la interpretabilidad científica de la predicción de la IA.
              </p>
              <p>
                El rigor analítico exige el uso de algoritmos de retropropagación como <strong>Grad-CAM (Gradient-weighted Class Activation Mapping)</strong>. Grad-CAM calcula el gradiente del score final de clasificación con respecto a los mapas de características de la última capa convolucional, identificando espacialmente qué distribuciones de píxeles (ej. la curvatura anómala de un arco celeste) maximizaron la probabilidad de la clase positiva ("Lente").
              </p>
              <p className="text-pink-400/90 bg-pink-400/10 p-3 rounded-lg border border-pink-400/20 text-sm mt-3">
                <strong>Estado de Implementación:</strong> En la etapa inicial actual del pipeline, el mapa renderizado actúa como un <em>placeholder</em> estructural para validar el Frontend. La integración computacional del tensor Grad-CAM en la inferencia real del servidor FastAPI está planificada para el próximo ciclo de desarrollo.
              </p>
            </div>
          </section>

          {/* Section 4 */}
          <section className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-3 mb-4">
              <Telescope className="w-6 h-6 text-green-400" />
              Cosmología y Fotometría: Redshift (z) y Magnitud (g)
            </h2>
            <div className="text-slate-300 space-y-3 leading-relaxed">
              <ul className="list-disc pl-5 space-y-4">
                <li>
                  <strong>Redshift (z):</strong> Representa el desplazamiento Doppler cosmológico y relativista. Su valor es estrictamente necesario en el marco del modelo cosmológico ΛCDM estándar para derivar las Distancias de Diámetro Angular hacia la lente (D<sub>d</sub>) y la fuente (D<sub>s</sub>). Sin estas distancias, la relación entre el Radio de Einstein aparente y la masa física de la galaxia resulta matemáticamente indeterminable.
                </li>
                <li>
                  <strong>Magnitud Aparente de Modelo (g):</strong> Es una medida logarítmica (m = -2.5 log₁₀(F/F₀)) del flujo incidente detectado en el filtro g (4000-5500 Å). Se utiliza en astrofísica observacional, junto con el Módulo de Distancia derivado del Redshift, para calcular la Luminosidad Intrínseca y, en consecuencia, inferir la Masa Estelar inicial de la galaxia deflectora.
                </li>
              </ul>
            </div>
          </section>

          {/* Section 5 */}
          <section className="bg-white/[0.02] border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h2 className="text-2xl font-semibold text-slate-100 flex items-center gap-3 mb-4">
              <Atom className="w-6 h-6 text-orange-400" />
              Fundamentos Analíticos
            </h2>
            <div className="text-slate-300 space-y-3 leading-relaxed">
              <p>
                La teoría subyacente deriva de la <strong>Relatividad General</strong>, donde la métrica del espacio-tiempo es perturbada localmente por un pozo de potencial gravitacional masivo. El Radio de Einstein efectivo (θ<sub>E</sub>) en un sistema de lente perfecta (alineación absoluta a lo largo del eje óptico) se define rigurosamente en radianes como:
              </p>
              <div className="bg-black/40 p-4 rounded-lg font-mono text-center text-lg text-slate-200 border border-white/5 my-4 overflow-x-auto">
                θ<sub>E</sub> = √( (4GM / c²) · (D<sub>ds</sub> / (D<sub>d</sub> · D<sub>s</sub>)) )
              </div>
              <p>
                Donde <strong>G</strong> es la constante gravitacional, <strong>M</strong> es la masa encerrada, <strong>c</strong> la velocidad de la luz, y las <strong>D</strong> representan las Distancias de Diámetro Angular dependientes del Redshift (z).
              </p>
              <div className="mt-5 pt-4 border-t border-white/10 flex flex-col gap-3 text-sm text-blue-300">
                <a href="https://arxiv.org/abs/1803.09746" target="_blank" rel="noopener noreferrer" className="hover:text-blue-200 hover:underline flex items-center gap-2">
                  <FileText className="w-4 h-4" /> lenstronomy: Multi-purpose gravitational lens modeling software (Birrer & Amara, 2018)
                </a>
                <a href="https://arxiv.org/abs/1512.03385" target="_blank" rel="noopener noreferrer" className="hover:text-blue-200 hover:underline flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Deep Residual Learning for Image Recognition (He et al., 2016)
                </a>
                <a href="https://arxiv.org/abs/1610.02391" target="_blank" rel="noopener noreferrer" className="hover:text-blue-200 hover:underline flex items-center gap-2">
                  <FileText className="w-4 h-4" /> Grad-CAM: Visual Explanations from Deep Networks (Selvaraju et al., 2017)
                </a>
              </div>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
