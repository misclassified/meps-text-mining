import argparse
import gradio as gr


def summarize(input):
    output = 'this is just a mirror' + input 
    return output

    
def main():

    parser = argparse.ArgumentParser(description='Interface for Meps speeches summary')
    parser.add_argument('--explain', help = 'Interface for Meps speeches summary using gradio')
    args = parser.parse_args()

    if args.explain:
        print("Minimal Gradio interface")

    gr.close_all()
    demo = gr.Interface(fn=summarize, inputs="text", outputs="text")
    demo.launch(share=True, server_port=5555)


if __name__ == "__main__":
    main()