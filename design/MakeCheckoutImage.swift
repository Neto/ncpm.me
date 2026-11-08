// Product image for the Stripe checkout page: app icon, the app name in bold type, and the tagline.
// Usage: swift design/MakeCheckoutImage.swift <icon-1024.png> <Name> <tagline> <output.png>
// The background is transparent, so the image sits on Stripe's white checkout panel.
import SwiftUI

struct CheckoutArt: View {
    let icon: NSImage
    let name: String
    let tagline: String

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // The icon file has a 100 point margin around the squircle on a 1024 canvas.
            Image(nsImage: icon)
                .resizable()
                .frame(width: 820, height: 820)
                .padding(.leading, -80)
                .padding(.top, -60)
            Text(name + ".")
                .font(.custom("HelveticaNeue-Bold", size: 230))
                .tracking(-9)
                .foregroundStyle(.black)
                .padding(.top, -40)
            Text(tagline)
                .font(.system(size: 50))
                .foregroundStyle(Color(red: 0.43, green: 0.43, blue: 0.45))
                .frame(width: 700, alignment: .leading)
                .padding(.top, 18)
        }
        .padding(.leading, 40)
        .frame(width: 900, height: 1200, alignment: .topLeading)
    }
}

@MainActor
func render() throws {
    let args = CommandLine.arguments
    guard args.count == 5, let icon = NSImage(contentsOfFile: args[1]) else {
        fputs("Usage: MakeCheckoutImage.swift <icon.png> <Name> <tagline> <output.png>\n", stderr)
        exit(1)
    }
    let renderer = ImageRenderer(content: CheckoutArt(icon: icon, name: args[2], tagline: args[3]))
    renderer.scale = 1
    guard let image = renderer.cgImage,
          let png = NSBitmapImageRep(cgImage: image).representation(using: .png, properties: [:]) else {
        fatalError("Failed to render the image")
    }
    try png.write(to: URL(filePath: args[4]))
}

try MainActor.assumeIsolated { try render() }
