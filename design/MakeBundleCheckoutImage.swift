// Product image for the bundle on the Stripe checkout page: both app icons, the bundle name, and the tagline.
// Usage: swift design/MakeBundleCheckoutImage.swift <spin-icon.png> <grabb-icon.png> <Name> <tagline> <output.png>
// Same layout and type as MakeCheckoutImage.swift. The background is transparent.
import SwiftUI

struct BundleArt: View {
    let icons: [NSImage]
    let name: String
    let tagline: String

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Each icon file has a 100 point margin around the squircle on a 1024 canvas.
            HStack(spacing: -70) {
                ForEach(icons.indices, id: \.self) { i in
                    Image(nsImage: icons[i])
                        .resizable()
                        .frame(width: 520, height: 520)
                }
            }
            .padding(.leading, -50)
            .padding(.top, 40)
            Text(name)
                .font(.custom("HelveticaNeue-Bold", size: 150))
                .tracking(-6)
                .foregroundStyle(.black)
                .padding(.top, 10)
            Text(tagline)
                .font(.system(size: 50))
                .foregroundStyle(Color(red: 0.43, green: 0.43, blue: 0.45))
                .frame(width: 760, alignment: .leading)
                .padding(.top, 18)
        }
        .padding(.leading, 40)
        .frame(width: 900, height: 1200, alignment: .topLeading)
    }
}

@MainActor
func render() throws {
    let args = CommandLine.arguments
    guard args.count == 6,
          let spin = NSImage(contentsOfFile: args[1]),
          let grabb = NSImage(contentsOfFile: args[2]) else {
        fputs("Usage: MakeBundleCheckoutImage.swift <spin.png> <grabb.png> <Name> <tagline> <output.png>\n", stderr)
        exit(1)
    }
    let renderer = ImageRenderer(content: BundleArt(icons: [spin, grabb], name: args[3], tagline: args[4]))
    renderer.scale = 1
    guard let image = renderer.cgImage,
          let png = NSBitmapImageRep(cgImage: image).representation(using: .png, properties: [:]) else {
        fatalError("Failed to render the image")
    }
    try png.write(to: URL(filePath: args[5]))
}

try MainActor.assumeIsolated { try render() }
