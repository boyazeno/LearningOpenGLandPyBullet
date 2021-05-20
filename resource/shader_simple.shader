#shader Vertex
#version 330 core
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
uniform mat4 u_MVP;
uniform mat4 u_Model;
out vec3 VertexNormal;
out vec3 FragPos;
void main()
{
    gl_Position  = u_MVP*vec4(position,1.0);
    VertexNormal = normal;
    FragPos = vec3(vec4(position, 1.0));
}

#shader Fragment
#version 330 core
in vec3 VertexNormal;
in vec3 FragPos;
uniform vec4 u_Color;
uniform vec3 u_LightColor;
uniform vec3 u_LightPose;
uniform float u_Ambient;
void main()
{
  vec3 norm = normalize(VertexNormal);
  vec3 lightDir = normalize(u_LightPose - FragPos);
  float diff = max(dot(norm, lightDir), 0.0);
  vec3 diffuse = diff * u_LightColor;
  vec3 result = (u_Ambient + diffuse) * u_Color.rgb;
  gl_FragColor = vec4(result, 1.0);
}
