#shader Vertex
#version 330 core
layout(location = 0) in vec2 position;
layout(location = 1) in vec2 textureCoordinate;
uniform mat4 u_MVP;
out vec2 v_TextureCoordinate;
void main()
{
    gl_Position  = u_MVP*vec4(position,0.0,1.0);
    v_TextureCoordinate = textureCoordinate;
}

#shader Fragment
#version 330 core
out vec4 color;

in vec2 v_TextureCoordinate;
uniform vec4 u_Color;
uniform sampler2D u_Texture;
void main()
{
  vec4 textureColor = texture2D(u_Texture,v_TextureCoordinate);
  gl_FragColor = textureColor;
}
